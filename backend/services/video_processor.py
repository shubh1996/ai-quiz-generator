import os
import re
import yt_dlp
from pathlib import Path
import tempfile
import asyncio
from typing import Optional, Dict
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

# Import YouTube API service (optional - will gracefully handle if not available)
try:
    from services.youtube_api_service import YouTubeAPIService
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️ google-api-python-client not installed - YouTube API disabled")

# Import third-party transcript API service (for cloud/production reliability)
try:
    from services.transcript_api_service import TranscriptAPIService
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False
    print("⚠️ transcript_api_service not available")


class VideoProcessingResult(BaseModel):
    """Result of video processing"""
    transcript: str
    title: Optional[str] = None
    duration: Optional[int] = None
    platform: Optional[str] = None


class VideoProcessor:
    """Service for processing video URLs and extracting transcripts"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="quiz_videos_")
        self.max_duration = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "7200"))  # 2 hours default

        # Initialize YouTube API service if available and configured
        self.youtube_api = None
        if YOUTUBE_API_AVAILABLE:
            try:
                self.youtube_api = YouTubeAPIService()
                print("✓ YouTube Data API v3 service enabled")
            except ValueError as e:
                print(f"⚠️ YouTube API key not configured: {e}")
            except Exception as e:
                print(f"⚠️ YouTube API initialization failed: {e}")

        # Initialize third-party transcript API (most reliable for cloud servers)
        self.transcript_api = None
        if TRANSCRIPT_API_AVAILABLE:
            try:
                self.transcript_api = TranscriptAPIService()
            except Exception as e:
                print(f"⚠️ Transcript API initialization failed: {e}")

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
        Try to get transcript using multiple methods:
        1. YouTube Data API v3 (if configured) - verifies video exists and has captions
        2. youtube-transcript-api - fetches actual captions (free, no auth needed)
        3. yt-dlp subtitle extraction - more robust against bot detection
        """
        try:
            video_id = self.extract_youtube_video_id(url)
            if not video_id:
                return None

            # Method 1: Try YouTube Data API v3 first (if available)
            if self.youtube_api:
                print(f"🔍 Checking video via YouTube Data API v3: {video_id}")
                api_info = self.youtube_api.get_video_info(url)

                if api_info:
                    if not api_info.get('has_captions'):
                        print(f"⚠️ Video has no captions according to YouTube API")
                        return None
                    else:
                        print(f"✓ YouTube API confirmed captions exist, attempting download...")
                else:
                    print(f"⚠️ Could not verify video via YouTube API, trying anyway...")

            # Method 2: youtube-transcript-api (free, no auth, but may be blocked on cloud servers)
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

            if transcript_list:
                # Combine all transcript entries
                transcript_text = " ".join([entry['text'] for entry in transcript_list])

                if transcript_text:
                    print("✓ Successfully fetched transcript via YouTube Transcript API")
                    return {
                        'transcript': transcript_text,
                        'method': 'youtube_transcript_api'
                    }

            # Method 3: If youtube-transcript-api failed (likely bot detection), try yt-dlp
            print(f"⚠️ YouTube Transcript API failed, trying yt-dlp subtitle extraction...")
            yt_dlp_result = await self._try_yt_dlp_subtitles(url, video_id)
            if yt_dlp_result:
                return yt_dlp_result

            # Method 4: If all free methods failed, try RapidAPI (most reliable for cloud servers)
            rapidapi_result = await self._try_rapidapi_transcript(video_id)
            if rapidapi_result:
                return rapidapi_result

            return None

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"⚠️ YouTube Transcript API failed: {str(e)}")
            # Try yt-dlp as fallback
            video_id = self.extract_youtube_video_id(url)
            if video_id:
                yt_dlp_result = await self._try_yt_dlp_subtitles(url, video_id)
                if yt_dlp_result:
                    return yt_dlp_result
                # Try RapidAPI as final fallback
                rapidapi_result = await self._try_rapidapi_transcript(video_id)
                if rapidapi_result:
                    return rapidapi_result
            return None
        except Exception as e:
            # Detect specific YouTube blocking/parsing errors
            error_msg = str(e)
            if "ParseError" in str(type(e)) or "no element found" in error_msg:
                print(f"⚠️ YouTube Transcript API: Video transcript is blocked or unavailable")
            else:
                print(f"⚠️ YouTube Transcript API error: {error_msg}")

            # Try yt-dlp as fallback for bot detection issues
            video_id = self.extract_youtube_video_id(url)
            if video_id:
                yt_dlp_result = await self._try_yt_dlp_subtitles(url, video_id)
                if yt_dlp_result:
                    return yt_dlp_result
                # Try RapidAPI as final fallback
                rapidapi_result = await self._try_rapidapi_transcript(video_id)
                if rapidapi_result:
                    return rapidapi_result
            return None

    async def _try_rapidapi_transcript(self, video_id: str) -> Optional[Dict[str, any]]:
        """
        Try to fetch transcript using RapidAPI's YouTube Transcripts service.
        This is the most reliable method for cloud servers as it bypasses bot detection.
        """
        if not self.transcript_api or not self.transcript_api.is_available():
            return None

        try:
            result = await self.transcript_api.get_transcript(video_id)
            return result
        except Exception as e:
            print(f"⚠️ RapidAPI transcript fetch failed: {e}")
            return None

    async def _try_yt_dlp_subtitles(self, url: str, video_id: str) -> Optional[Dict[str, any]]:
        """
        Try to extract subtitles using yt-dlp with enhanced bot evasion.
        This is more robust than youtube-transcript-api on cloud servers.
        """
        try:
            print(f"🔄 Attempting yt-dlp subtitle extraction with bot evasion...")

            # Enhanced options for bot detection evasion
            subtitle_opts = {
                'quiet': True,
                'no_warnings': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-orig'],
                'skip_download': True,
                'outtmpl': f'{self.temp_dir}/%(id)s',
                # Enhanced bot evasion settings
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                },
                # Use cookies from browser if available
                'cookiesfrombrowser': ('chrome',) if os.path.exists(os.path.expanduser('~/.config/google-chrome')) else None,
            }

            # Remove None values
            subtitle_opts = {k: v for k, v in subtitle_opts.items() if v is not None}

            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Check if subtitles were downloaded
                actual_video_id = info.get('id', video_id)

                # Try different subtitle file extensions and language codes
                subtitle_patterns = [
                    f'{actual_video_id}.en.vtt',
                    f'{actual_video_id}.en-US.vtt',
                    f'{actual_video_id}.en-GB.vtt',
                    f'{actual_video_id}.en-orig.vtt',
                    f'{actual_video_id}.en.srt',
                ]

                for pattern in subtitle_patterns:
                    subtitle_path = f"{self.temp_dir}/{pattern}"
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

                        if transcript and len(transcript) > 100:  # Ensure we have meaningful content
                            print(f"✓ Successfully extracted subtitles via yt-dlp ({pattern})")
                            return {
                                'transcript': transcript,
                                'method': 'yt_dlp_subtitles'
                            }

            print(f"⚠️ yt-dlp could not find subtitle files")
            return None

        except Exception as e:
            error_msg = str(e).lower()
            if 'bot' in error_msg or 'sign in' in error_msg:
                print(f"⚠️ yt-dlp blocked by bot detection: {e}")
            else:
                print(f"⚠️ yt-dlp subtitle extraction failed: {e}")
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
            # Enhanced options for better bot detection evasion
            common_opts = {
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'web'],  # iOS client is less likely to be blocked
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

            # Step 4: If no subtitles found, raise error (no Whisper fallback)
            if not transcript:
                raise Exception(
                    "Could not extract transcript from video. "
                    "Please ensure the video has English captions/subtitles enabled. "
                    "Educational channels like Khan Academy, CrashCourse, and TED-Ed usually have captions."
                )

            return VideoProcessingResult(
                transcript=transcript,
                title=title,
                duration=duration,
                platform=platform
            )

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # Provide user-friendly error messages for common issues
            if "bot" in error_msg.lower() or "sign in" in error_msg.lower():
                raise Exception(
                    "YouTube has blocked access to this video. This can happen with certain videos. "
                    "Workarounds: 1) Use a different educational video from verified channels, "
                    "2) Download the video manually and upload the file instead, "
                    "3) Try a video with captions/subtitles enabled. "
                    "Educational channels like Khan Academy, CrashCourse, and TED-Ed usually work best."
                )
            else:
                raise Exception(f"Failed to download video: {error_msg}")
        except Exception as e:
            raise Exception(f"Video processing error: {str(e)}")

    async def _try_extract_subtitles(self, url: str, common_opts: dict) -> Optional[str]:
        """
        Try to extract existing subtitles/captions from video.
        This is less likely to be blocked than downloading audio.
        """
        try:
            # Enhanced subtitle options with better bot evasion
            subtitle_opts = {
                **common_opts,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'en-orig'],
                'skip_download': True,
                'outtmpl': f'{self.temp_dir}/%(id)s',
                # Override with enhanced bot evasion
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
            }

            with yt_dlp.YoutubeDL(subtitle_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Check if subtitles were downloaded
                video_id = info.get('id', 'video')

                # Try different subtitle file extensions
                for ext in ['.en.vtt', '.en-US.vtt', '.en-GB.vtt', '.en-orig.vtt', '.en.srt']:
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

                        if transcript and len(transcript) > 100:
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


    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
