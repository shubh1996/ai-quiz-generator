import os
import httpx
import json
from typing import Optional


class ContentSafetyService:
    """
    Service for filtering inappropriate content based on age mode.
    Ensures kid-safe content when age_mode is set to under 18.
    """

    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.base_url = "https://api.perplexity.ai/chat/completions"

    async def check_content_safety(
        self,
        content: str,
        age_mode: str = "18+",  # "kids" or "18+"
        source_url: Optional[str] = None
    ) -> dict:
        """
        Check if content is appropriate for the specified age mode.

        Args:
            content: The content text to check
            age_mode: "kids" (under 18) or "18+" (adults)
            source_url: Optional URL for additional context

        Returns:
            {
                "is_safe": bool,
                "rejection_reason": str or None,
                "confidence": float (0-100),
                "flagged_topics": list of strings
            }
        """
        if not self.perplexity_api_key:
            # If no API key, allow content but flag as unverified
            print("⚠️ Content safety check skipped - no API key")
            return {
                "is_safe": True,
                "rejection_reason": None,
                "confidence": 0,
                "flagged_topics": []
            }

        # For kids mode, use strict filtering
        if age_mode == "kids":
            return await self._check_kid_safe_content(content, source_url)
        else:
            # For 18+ mode, still filter extremely inappropriate content
            return await self._check_adult_content(content, source_url)

    async def _check_kid_safe_content(self, content: str, source_url: Optional[str]) -> dict:
        """
        Strict content filtering for users under 18.
        Blocks: violence, substances, abuse, vulgar language, mature themes, etc.
        """
        try:
            # Truncate content for API efficiency
            content_sample = content[:2000]

            prompt = f"""Analyze this content for child safety (under 18). This is CRITICAL for protecting children.

Content to analyze:
{content_sample}

Source URL: {source_url or "Not provided"}

Check if the content contains ANY of the following INAPPROPRIATE topics or themes:

STRICTLY FORBIDDEN for kids:
1. Violence, gore, weapons, fighting, war, harm to people/animals
2. Drugs, alcohol, smoking, vaping, substance abuse of any kind
3. Sexual content, mature themes, dating, relationships beyond friendship
4. Profanity, vulgar language, cursing, inappropriate slang
5. Abuse (physical, emotional, verbal), bullying, harassment
6. Horror, scary themes, disturbing imagery
7. Gambling, betting, adult gaming
8. Dangerous activities, self-harm, suicide
9. Hate speech, discrimination, offensive content
10. Political controversy, sensitive social issues
11. Adult products, services, or advertisements

ALLOWED for kids:
- Educational content (science, math, history, geography, etc.)
- Age-appropriate entertainment (cartoons, kids shows, family movies)
- Arts, crafts, music, sports
- Nature, animals, space
- Technology basics, coding for kids
- Health and hygiene education
- Friendship, kindness, positive values

Return ONLY valid JSON:
{{
    "is_safe": false if ANY forbidden topic is detected, true if completely safe,
    "rejection_reason": "specific reason why content is unsafe (or null if safe)",
    "confidence": 0-100 (how confident you are in this assessment),
    "flagged_topics": ["list of specific inappropriate topics found"]
}}

BE EXTREMELY STRICT. When in doubt, mark as unsafe. Children's safety is paramount."""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a strict content safety moderator for children under 18. Your job is to protect children from ALL inappropriate content. Be extremely conservative - when in doubt, reject the content. Return ONLY valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,  # Low temperature for consistent results
                        "max_tokens": 500
                    },
                    timeout=15.0
                )

            if response.status_code == 200:
                result = response.json()
                safety_text = result['choices'][0]['message']['content']

                # Clean markdown if present
                safety_text = safety_text.strip()
                if safety_text.startswith('```json'):
                    safety_text = safety_text[7:]
                if safety_text.startswith('```'):
                    safety_text = safety_text[3:]
                if safety_text.endswith('```'):
                    safety_text = safety_text[:-3]
                safety_text = safety_text.strip()

                safety_result = json.loads(safety_text)

                if not safety_result.get("is_safe", True):
                    print(f"🚫 KID-SAFE FILTER: Content blocked - {safety_result.get('rejection_reason')}")
                    print(f"   Flagged topics: {', '.join(safety_result.get('flagged_topics', []))}")
                else:
                    print("✅ KID-SAFE FILTER: Content approved")

                return safety_result
            else:
                print(f"⚠️ Safety check API failed: {response.status_code}")
                # On API failure, default to BLOCKING content in kid mode for safety
                return {
                    "is_safe": False,
                    "rejection_reason": "Unable to verify content safety - blocked for child protection",
                    "confidence": 0,
                    "flagged_topics": ["api_failure"]
                }

        except Exception as e:
            print(f"⚠️ Safety check error: {e}")
            # On error in kid mode, default to BLOCKING for safety
            return {
                "is_safe": False,
                "rejection_reason": "Content safety verification failed - blocked for child protection",
                "confidence": 0,
                "flagged_topics": ["verification_error"]
            }

    async def _check_adult_content(self, content: str, source_url: Optional[str]) -> dict:
        """
        Basic content filtering for 18+ users.
        Only blocks extremely inappropriate content (illegal, harmful).
        """
        try:
            content_sample = content[:2000]

            prompt = f"""Analyze this content for extreme inappropriateness (18+ mode).

Content to analyze:
{content_sample}

Source URL: {source_url or "Not provided"}

Block ONLY if content contains:
1. Illegal activities or instructions
2. Extreme violence or gore
3. Explicit sexual content
4. Instructions for self-harm or harm to others
5. Hate speech or extremist content

Allow most educational, news, mature discussion content.

Return ONLY valid JSON:
{{
    "is_safe": true/false,
    "rejection_reason": "reason or null",
    "confidence": 0-100,
    "flagged_topics": ["list"]
}}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a content moderator for adult users. Block only extremely inappropriate content. Return ONLY valid JSON."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 300
                    },
                    timeout=15.0
                )

            if response.status_code == 200:
                result = response.json()
                safety_text = result['choices'][0]['message']['content']

                safety_text = safety_text.strip()
                if safety_text.startswith('```json'):
                    safety_text = safety_text[7:]
                if safety_text.startswith('```'):
                    safety_text = safety_text[3:]
                if safety_text.endswith('```'):
                    safety_text = safety_text[:-3]
                safety_text = safety_text.strip()

                safety_result = json.loads(safety_text)

                if not safety_result.get("is_safe", True):
                    print(f"🚫 18+ FILTER: Content blocked - {safety_result.get('rejection_reason')}")

                return safety_result
            else:
                # On API failure for 18+, allow content (less strict)
                return {
                    "is_safe": True,
                    "rejection_reason": None,
                    "confidence": 0,
                    "flagged_topics": []
                }

        except Exception as e:
            print(f"⚠️ Safety check error: {e}")
            # On error for 18+, allow content
            return {
                "is_safe": True,
                "rejection_reason": None,
                "confidence": 0,
                "flagged_topics": []
            }
