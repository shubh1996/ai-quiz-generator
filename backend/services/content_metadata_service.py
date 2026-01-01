import os
import httpx
import json
import re
from typing import Optional
from models.quiz import ContentMetadata


class ContentMetadataService:
    """Service for extracting and generating content metadata"""

    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

    async def generate_metadata(
        self,
        content: str,
        source_type: str,
        source_identifier: str,
        title: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> ContentMetadata:
        """
        Generate content metadata including title, description, categories, etc.

        Args:
            content: The actual content text
            source_type: video_url, video_file, document_file, web_url
            source_identifier: URL or filename
            title: Optional pre-extracted title
            duration_seconds: Optional duration in seconds (for videos)
        """

        # Calculate duration in minutes
        duration_minutes = None
        if duration_seconds:
            duration_minutes = round(duration_seconds / 60)
        elif source_type in ["document_file", "web_url"]:
            # Estimate reading time (200 words per minute)
            word_count = len(content.split())
            duration_minutes = max(1, round(word_count / 200))

        # Determine media type
        if source_type in ["video_url", "video_file"]:
            media_type = "video"
        elif source_type == "web_url":
            media_type = "article"
        else:
            media_type = "document"

        # Extract creator name for YouTube
        creator_name = None
        if "youtube.com" in source_identifier or "youtu.be" in source_identifier:
            creator_name = self._extract_youtube_channel(source_identifier)

        # Generate thumbnail URL
        thumbnail_url = None
        if "youtube.com" in source_identifier or "youtu.be" in source_identifier:
            video_id = self._extract_youtube_video_id(source_identifier)
            if video_id:
                thumbnail_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

        # Generate title and description using AI
        ai_metadata = await self._generate_ai_metadata(content, title)

        return ContentMetadata(
            title=ai_metadata.get("title", title or "Untitled Content"),
            description=ai_metadata.get("description", "Educational content"),
            media_link=source_identifier,
            duration=duration_minutes,
            suggested_categories=ai_metadata.get("categories", ["General Education"]),
            suggested_media_type=media_type,
            creator_name=creator_name,
            thumbnail_url=thumbnail_url
        )

    async def _generate_ai_metadata(self, content: str, existing_title: Optional[str] = None) -> dict:
        """Use AI to generate title, description, and categories"""

        if not self.perplexity_api_key:
            # Fallback without AI
            return {
                "title": existing_title or "Educational Content",
                "description": content[:200] + "..." if len(content) > 200 else content,
                "categories": ["General Education"]
            }

        try:
            # Truncate content for API efficiency
            content_sample = content[:1500]

            prompt = f"""Analyze this educational content and provide metadata:

Content:
{content_sample}

Generate a JSON response with:
1. A clear, concise title (max 80 characters)
2. A compelling 2-3 sentence description summarizing the key topics
3. 2-4 relevant educational categories

Return ONLY valid JSON:
{{
    "title": "Content Title Here",
    "description": "A 2-3 sentence summary of the content...",
    "categories": ["Category 1", "Category 2", "Category 3"]
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a content analyst. Return ONLY valid JSON without markdown."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500
                    },
                    timeout=15.0
                )

            if response.status_code == 200:
                result = response.json()
                metadata_text = result['choices'][0]['message']['content']

                # Clean markdown if present
                metadata_text = metadata_text.strip()
                if metadata_text.startswith('```json'):
                    metadata_text = metadata_text[7:]
                if metadata_text.startswith('```'):
                    metadata_text = metadata_text[3:]
                if metadata_text.endswith('```'):
                    metadata_text = metadata_text[:-3]
                metadata_text = metadata_text.strip()

                metadata = json.loads(metadata_text)
                print("✓ AI-generated content metadata")
                return metadata
            else:
                print(f"⚠️ AI metadata generation failed: {response.status_code}")
                raise Exception("AI failed")

        except Exception as e:
            print(f"⚠️ Could not generate AI metadata: {e}")
            # Fallback
            return {
                "title": existing_title or "Educational Content",
                "description": content[:200] + "..." if len(content) > 200 else content,
                "categories": ["General Education"]
            }

    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
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

    def _extract_youtube_channel(self, url: str) -> Optional[str]:
        """Try to extract YouTube channel name from URL"""
        # This is a simple extraction - would need YouTube API for reliable channel names
        # For now, return None and let it be filled in later if needed
        return None
