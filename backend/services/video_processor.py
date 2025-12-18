import os
import re
import yt_dlp
from openai import AsyncOpenAI
from pathlib import Path
import tempfile
import asyncio
from typing import Optional, Dict
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class VideoProcessingResult(BaseModel):
    """Result of video processing"""
    transcript: str
    title: Optional[str] = None
    duration: Optional[int] = None
    platform: Optional[str] = None


class VideoProcessor:
    """Service for processing video URLs and extracting transcripts"""

    def __init__(self, openai_api_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.temp_dir = tempfile.mkdtemp(prefix="quiz_videos_")
        self.max_duration = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "7200"))  # 2 hours default

    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        url_lower = url.lower()

        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "YouTube"
        elif "vimeo.com" in url_lower:
            return "Vimeo"
        elif "dailymotion.com" in url_lower:
            return "Dailymotion"
        elif "twitch.tv" in url_lower:
            return "Twitch"
        else:
            return "Unknown"

    def extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        # Match various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def _try_youtube_transcript_api(self, url: str) -> Optional[Dict[str, any]]:
        """
        Try to get transcript using youtube-transcript-api.
        This is more reliable than yt-dlp for getting transcripts as it doesn't download video.
        """
        try:
            video_id = self.extract_youtube_video_id(url)
            if not video_id:
                return None

            print(f"🔍 Attempting to fetch transcript via YouTube Transcript API for video: {video_id}")

            # Try multiple language codes and auto-generated captions
            language_attempts = [
                ['en'],           # English
                ['en-US'],        # US English
                ['en-GB'],        # British English
                ['a.en'],         # Auto-generated English
            ]

            transcript_list = None
            for languages in language_attempts:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
                    if transcript_list:
                        print(f"✓ Found transcript with languages: {languages}")
                        break
                except:
                    continue

            # If specific languages failed, try to get any available transcript
            if not transcript_list:
                try:
                    transcript_dict = YouTubeTranscriptApi.list_transcripts(video_id)
                    # Try to find any English transcript (manual or auto-generated)
                    for transcript in transcript_dict:
                        if transcript.language_code.startswith('en'):
                            transcript_list = transcript.fetch()
                            print(f"✓ Found transcript: {transcript.language} ({transcript.language_code})")
                            break
                except:
                    pass

            if not transcript_list:
                return None

            # Combine all transcript entries
            transcript_text = " ".join([entry['text'] for entry in transcript_list])

            if transcript_text:
                print("✓ Successfully fetched transcript via YouTube Transcript API")
                return {
                    'transcript': transcript_text,
                    'method': 'youtube_transcript_api'
                }

            return None

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"⚠️ YouTube Transcript API failed: {str(e)}")
            return None
        except Exception as e:
            print(f"⚠️ YouTube Transcript API error: {str(e)}")
            return None

    async def process_video_url(self, url: str) -> VideoProcessingResult:
        """
        Process a video URL with multiple fallback strategies:
        1. For YouTube: Try YouTube Transcript API first (fastest, no bot detection)
        2. Try yt-dlp to extract metadata and subtitles
        3. If yt-dlp fails due to bot detection, use basic metadata
        4. Fall back to audio download and Whisper transcription
        """
        try:
            platform = self.detect_platform(url)
            title = "Unknown"
            duration = 0
            transcript = None

            # Step 1: For YouTube videos, try YouTube Transcript API first
            if platform == "YouTube":
                yt_api_result = await self._try_youtube_transcript_api(url)
                if yt_api_result:
                    # Success! We have the transcript, now just get metadata
                    try:
                        # Try to get basic metadata without downloading
                        video_id = self.extract_youtube_video_id(url)
                        title = f"YouTube Video {video_id}" if video_id else "YouTube Video"

                        # Try to get full metadata if possible
                        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                            try:
                                info = ydl.extract_info(url, download=False)
                                if info:
                                    title = info.get('title', title)
                                    duration = info.get('duration', 0)
                            except:
                                pass  # If metadata fails, continue with what we have

                    except:
                        pass  # Continue with transcript even if metadata fails

                    return VideoProcessingResult(
                        transcript=yt_api_result['transcript'],
                        title=title,
                        duration=duration,
                        platform=platform
                    )

            # Step 2: Try yt-dlp for non-YouTube or if Transcript API failed
            # Common options to avoid blocking
            common_opts = {
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                # Additional headers to avoid bot detection
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }

            # Try to extract video info
            try:
                with yt_dlp.YoutubeDL(common_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    if not info:
                        raise Exception("Failed to extract video information")

                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)

                    # Check duration limit
                    if duration > self.max_duration:
                        raise Exception(f"Video too long ({duration}s). Maximum allowed: {self.max_duration}s")
            except Exception as e:
                # If bot detection blocks us, we can still try to continue
                if "bot" in str(e).lower() or "sign in" in str(e).lower():
                    print(f"⚠️ yt-dlp metadata extraction blocked by bot detection, continuing with transcript attempts...")
                else:
                    raise

            # Step 3: Try to extract subtitles/captions
            if not transcript:
                transcript = await self._try_extract_subtitles(url, common_opts)

            # Step 4: If no subtitles, fall back to audio transcription
            if not transcript:
                print("⚠️ No subtitles found, attempting audio download and transcription...")
                transcript = await self._transcribe_from_audio(url, common_opts)

            return VideoProcessingResult(
                transcript=transcript,
                title=title,
                duration=duration,
                platform=platform
            )

        except yt_dlp.utils.DownloadError as e:
            raise Exception(f"Failed to download video: {str(e)}")
        except Exception as e:
            raise Exception(f"Video processing error: {str(e)}")

    async def _try_extract_subtitles(self, url: str, common_opts: dict) -> Optional[str]:
        """
        Try to extract existing subtitles/captions from video.
        This is less likely to be blocked than downloading audio.
        """
        try:
            subtitle_opts = {
                **common_opts,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB'],
                'skip_download': True,
                'outtmpl': f'{self.temp_dir}/%(id)s',
            }

            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Check if subtitles were downloaded
                video_id = info.get('id', 'video')

                # Try different subtitle file extensions
                for ext in ['.en.vtt', '.en-US.vtt', '.en-GB.vtt', '.en.srt']:
                    subtitle_path = f"{self.temp_dir}/{video_id}{ext}"
                    if os.path.exists(subtitle_path):
                        with open(subtitle_path, 'r', encoding='utf-8') as f:
                            subtitle_content = f.read()

                        # Clean VTT/SRT format
                        transcript = self._clean_subtitle_text(subtitle_content)

                        # Cleanup subtitle file
                        try:
                            os.remove(subtitle_path)
                        except:
                            pass

                        if transcript:
                            print("✓ Successfully extracted subtitles")
                            return transcript

            return None
        except Exception as e:
            print(f"⚠️ Subtitle extraction failed: {str(e)}")
            return None

    def _clean_subtitle_text(self, subtitle_content: str) -> str:
        """Clean VTT/SRT subtitle formatting to get plain text"""
        import re

        # Remove WEBVTT header
        text = re.sub(r'^WEBVTT.*?\n\n', '', subtitle_content, flags=re.DOTALL)

        # Remove timestamp lines (e.g., "00:00:01.000 --> 00:00:05.000")
        text = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', text)

        # Remove cue identifiers (numbers)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)

        # Remove positioning tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove duplicate spaces and newlines
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' +', ' ', text)

        return text.strip()

    async def _transcribe_from_audio(self, url: str, common_opts: dict) -> str:
        """
        Download audio and transcribe using Whisper API.
        Fallback method when subtitles are not available.
        """
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'outtmpl': f'{self.temp_dir}/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        audio_file_path = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                download_info = ydl.extract_info(url, download=True)
                video_id = download_info.get('id', 'audio')
                audio_file_path = f"{self.temp_dir}/{video_id}.mp3"

            if not audio_file_path or not os.path.exists(audio_file_path):
                raise Exception("Failed to download audio from video")

            # Transcribe audio
            transcript = await self.transcribe_audio(audio_file_path)

            return transcript
        finally:
            # Cleanup audio file
            if audio_file_path:
                try:
                    os.remove(audio_file_path)
                except:
                    pass

    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using OpenAI Whisper API
        """
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )

            if isinstance(transcript, str):
                return transcript
            else:
                # Handle case where transcript is an object with text attribute
                return transcript.text if hasattr(transcript, 'text') else str(transcript)

        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
