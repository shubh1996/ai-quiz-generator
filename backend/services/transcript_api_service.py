"""
Third-party YouTube Transcript API Service

Uses RapidAPI's YouTube Transcripts API as a reliable fallback
when youtube-transcript-api and yt-dlp fail due to bot detection.

RapidAPI Pricing (as of 2025):
- Free: 100 requests/month
- PRO: $9/month for 1,000 requests
- ULTRA: $29/month for 10,000 requests (recommended)
- MEGA: $59/month for 50,000 requests
"""

import os
import httpx
from typing import Optional, Dict


class TranscriptAPIService:
    """
    Service for fetching YouTube transcripts via RapidAPI.
    This is the most reliable method for cloud/production servers
    as it bypasses YouTube's bot detection.
    """

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = "youtube-transcripts.p.rapidapi.com"
        self.base_url = f"https://{self.api_host}"

        if self.api_key:
            print("✓ RapidAPI YouTube Transcripts service enabled")
        else:
            print("⚠️ RAPIDAPI_KEY not configured - third-party transcript API disabled")

    def is_available(self) -> bool:
        """Check if the API is configured and available"""
        return bool(self.api_key)

    async def get_transcript(self, video_id: str, language: str = "en") -> Optional[Dict]:
        """
        Fetch transcript for a YouTube video using RapidAPI.

        Args:
            video_id: YouTube video ID (e.g., 'fNk_zzaMoSs')
            language: Language code (default: 'en')

        Returns:
            Dict with 'transcript' and 'method' keys, or None if failed
        """
        if not self.api_key:
            return None

        try:
            print(f"🌐 Fetching transcript via RapidAPI for video: {video_id}")

            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.api_host,
            }

            # RapidAPI YouTube Transcripts endpoint
            url = f"{self.base_url}/youtube/transcript"
            params = {
                "video_id": video_id,
                "lang": language,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()

                    # Handle different response formats
                    transcript_text = None

                    if isinstance(data, list):
                        # Response is a list of transcript segments
                        transcript_text = " ".join(
                            segment.get("text", "") for segment in data
                        )
                    elif isinstance(data, dict):
                        # Response is a dict with transcript data
                        if "transcript" in data:
                            transcript_text = data["transcript"]
                        elif "content" in data:
                            # Some APIs return content array
                            content = data.get("content", [])
                            if isinstance(content, list):
                                transcript_text = " ".join(
                                    item.get("text", "") for item in content
                                )
                            else:
                                transcript_text = str(content)
                        elif "text" in data:
                            transcript_text = data["text"]

                    if transcript_text and len(transcript_text) > 100:
                        print(f"✓ Successfully fetched transcript via RapidAPI ({len(transcript_text)} chars)")
                        return {
                            "transcript": transcript_text,
                            "method": "rapidapi_transcript"
                        }
                    else:
                        print(f"⚠️ RapidAPI returned empty or short transcript")
                        return None

                elif response.status_code == 404:
                    print(f"⚠️ RapidAPI: No transcript found for video {video_id}")
                    return None
                elif response.status_code == 429:
                    print(f"⚠️ RapidAPI: Rate limit exceeded (upgrade plan or wait)")
                    return None
                elif response.status_code == 403:
                    print(f"⚠️ RapidAPI: Invalid API key or subscription expired")
                    return None
                else:
                    print(f"⚠️ RapidAPI error: {response.status_code} - {response.text[:200]}")
                    return None

        except httpx.TimeoutException:
            print(f"⚠️ RapidAPI request timed out")
            return None
        except Exception as e:
            print(f"⚠️ RapidAPI error: {str(e)}")
            return None


class SerpApiTranscriptService:
    """
    Alternative service using SerpApi for YouTube transcripts.
    More expensive but very reliable.

    Pricing (as of 2025):
    - Free: 250 searches/month
    - Starter: $25/month for 1,000 searches
    """

    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"

        if self.api_key:
            print("✓ SerpApi YouTube Transcripts service enabled")

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def get_transcript(self, video_id: str, language: str = "en") -> Optional[Dict]:
        """
        Fetch transcript using SerpApi's YouTube Transcript engine.
        """
        if not self.api_key:
            return None

        try:
            print(f"🌐 Fetching transcript via SerpApi for video: {video_id}")

            params = {
                "engine": "youtube_video_transcript",
                "v": video_id,
                "language_code": language,
                "api_key": self.api_key,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)

                if response.status_code == 200:
                    data = response.json()

                    # SerpApi returns transcript in 'transcript' array
                    transcript_segments = data.get("transcript", [])

                    if transcript_segments:
                        transcript_text = " ".join(
                            segment.get("snippet", "") for segment in transcript_segments
                        )

                        if transcript_text and len(transcript_text) > 100:
                            print(f"✓ Successfully fetched transcript via SerpApi ({len(transcript_text)} chars)")
                            return {
                                "transcript": transcript_text,
                                "method": "serpapi_transcript"
                            }

                    print(f"⚠️ SerpApi returned empty transcript")
                    return None

                else:
                    print(f"⚠️ SerpApi error: {response.status_code}")
                    return None

        except Exception as e:
            print(f"⚠️ SerpApi error: {str(e)}")
            return None
