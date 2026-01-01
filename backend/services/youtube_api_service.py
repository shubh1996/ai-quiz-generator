import os
import re
from typing import Optional, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeAPIService:
    """Service for accessing YouTube Data API v3 to get video captions"""

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not configured")

        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        print(f"✓ YouTube Data API v3 initialized")

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
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

    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video information using YouTube Data API v3

        Returns:
            Dict with 'video_id', 'title', 'duration', 'has_captions' keys, or None
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                print(f"⚠️ Could not extract video ID from URL: {url}")
                return None

            print(f"🔍 Fetching video info for: {video_id}")

            # Get video details (costs 1 unit)
            video_response = self.youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()

            if not video_response.get('items'):
                print(f"⚠️ Video not found: {video_id}")
                return None

            video_info = video_response['items'][0]
            title = video_info['snippet']['title']

            # Parse duration (ISO 8601 format like 'PT15M33S')
            duration_iso = video_info['contentDetails']['duration']
            duration = self._parse_duration(duration_iso)

            # Check for captions (costs 50 units)
            has_captions = False
            caption_language = None

            try:
                captions = self.youtube.captions().list(
                    part='snippet',
                    videoId=video_id
                ).execute()

                if captions.get('items'):
                    # Find English caption
                    for caption in captions['items']:
                        lang = caption['snippet']['language']
                        if lang.startswith('en'):
                            has_captions = True
                            caption_language = lang
                            print(f"✓ Found English captions: {lang}")
                            break

                    if not has_captions and captions['items']:
                        # Use first available caption if no English
                        has_captions = True
                        caption_language = captions['items'][0]['snippet']['language']
                        print(f"✓ Found captions in: {caption_language}")

            except HttpError as e:
                # Captions list might fail for some videos, continue anyway
                print(f"⚠️ Could not fetch caption info: {e}")

            result = {
                'video_id': video_id,
                'title': title,
                'duration': duration,
                'has_captions': has_captions,
                'caption_language': caption_language
            }

            print(f"✓ Video info retrieved: {title} ({duration}s, captions: {has_captions})")
            return result

        except HttpError as e:
            error_message = str(e)
            if 'quotaExceeded' in error_message:
                print(f"⚠️ YouTube API quota exceeded. Resets at midnight PT.")
            else:
                print(f"⚠️ YouTube API Error: {e}")
            return None
        except Exception as e:
            print(f"⚠️ YouTube API Service Error: {e}")
            return None

    def _parse_duration(self, duration_iso: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        # Example: 'PT15M33S' -> 933 seconds
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_iso)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    def check_quota_usage(self) -> Dict:
        """
        Return quota information

        Note: Actual quota usage is shown in Google Cloud Console
        """
        return {
            "daily_limit": 10000,
            "cost_per_video_info": 1,  # videos.list
            "cost_per_caption_check": 50,  # captions.list
            "estimated_daily_videos": 10000 // 51,  # ~196 videos/day with caption checks
            "note": "View actual usage at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas"
        }
