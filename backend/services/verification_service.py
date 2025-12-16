import json
import re
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional, Dict
from openai import AsyncOpenAI

from models.verification import (
    VerificationStatus,
    VerificationMetadata,
    EducationalAnalysis
)


# Educational platform whitelist
VERIFIED_EDUCATIONAL_PLATFORMS = {
    # Major MOOCs
    "coursera.org": {"name": "Coursera", "priority": 1},
    "edx.org": {"name": "edX", "priority": 1},
    "udacity.com": {"name": "Udacity", "priority": 1},
    "udemy.com": {"name": "Udemy", "priority": 2},
    "linkedin.com/learning": {"name": "LinkedIn Learning", "priority": 1},
    "skillshare.com": {"name": "Skillshare", "priority": 2},
    "pluralsight.com": {"name": "Pluralsight", "priority": 1},
    "datacamp.com": {"name": "DataCamp", "priority": 1},
    "codecademy.com": {"name": "Codecademy", "priority": 1},

    # Academic Institutions
    "mit.edu": {"name": "MIT", "priority": 1},
    "harvard.edu": {"name": "Harvard", "priority": 1},
    "stanford.edu": {"name": "Stanford", "priority": 1},
    "yale.edu": {"name": "Yale", "priority": 1},
    "berkeley.edu": {"name": "UC Berkeley", "priority": 1},
    "ox.ac.uk": {"name": "Oxford", "priority": 1},
    "cam.ac.uk": {"name": "Cambridge", "priority": 1},

    # YouTube Educational Channels
    "khanacademy.org": {"name": "Khan Academy", "priority": 1},

    # Language Learning
    "duolingo.com": {"name": "Duolingo", "priority": 1},
    "babbel.com": {"name": "Babbel", "priority": 1},
    "rosettastone.com": {"name": "Rosetta Stone", "priority": 1},

    # Professional Development
    "masterclass.com": {"name": "MasterClass", "priority": 2},
    "brillant.org": {"name": "Brilliant", "priority": 1},
}

# YouTube educational channel patterns and IDs
YOUTUBE_EDU_PATTERNS = [
    r"youtube\.com/edu",
    r"youtube\.com/user/khanacademy",
    r"youtube\.com/c/3blue1brown",
    r"youtube\.com/c/CrashCourse",
    r"youtube\.com/c/veritasium",
    r"youtube\.com/c/VSauce",
    r"youtube\.com/c/TED-Ed",
    r"youtube\.com/c/SmarterEveryDay",
]

# Known educational YouTube channel names (for watch URLs)
YOUTUBE_EDU_CHANNELS = [
    "Khan Academy",
    "3Blue1Brown",
    "CrashCourse",
    "Veritasium",
    "Vsauce",
    "TED-Ed",
    "MIT OpenCourseWare",
    "Stanford Online",
    "freeCodeCamp.org",
    "Computerphile",
    "Numberphile",
    "Physics Girl",
    "SmarterEveryDay",
    "MinutePhysics",
]


EDUCATIONAL_CLASSIFIER_SYSTEM_PROMPT = """You are an educational content quality assessor. Analyze the provided content and determine:

1. Is this content genuinely educational? (not entertainment, gossip, or promotional)
2. What is your confidence level (0-100)?
3. What topics does it cover?
4. What makes it educational?
5. Are there any non-educational red flags?

Educational criteria:
- Teaches skills, concepts, or knowledge
- Structured learning objectives
- Factual, researched information
- Academic or professional development focus
- Explanatory or instructional in nature

Non-educational red flags:
- Entertainment/comedy (primary purpose)
- Celebrity gossip or drama
- Product advertisements/promotions
- Clickbait or sensationalism
- Political propaganda without educational value
- Conspiracy theories
- Pure news reporting without educational analysis
- Gaming/streaming content without educational purpose
- Vlogs or personal lifestyle content

Return JSON format:
{
  "is_educational": bool,
  "confidence": float (0-100),
  "topics": [string],
  "educational_indicators": [string],
  "non_educational_flags": [string],
  "reasoning": string
}"""


class VerificationService:
    """Service for verifying educational content quality"""

    def __init__(self, openai_api_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.confidence_threshold = 70.0  # Minimum confidence to accept content

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ""

    def check_whitelist(self, url: Optional[str]) -> Optional[VerificationMetadata]:
        """
        Check if URL matches verified educational platform whitelist
        Returns VerificationMetadata if matched, None otherwise
        """
        if not url:
            return None

        domain = self._extract_domain(url)

        # Check direct domain matches
        for pattern, info in VERIFIED_EDUCATIONAL_PLATFORMS.items():
            if pattern in domain:
                return VerificationMetadata(
                    status=VerificationStatus.VERIFIED,
                    platform=info["name"],
                    verification_method="whitelist",
                    verified_at=datetime.now()
                )

        # Check YouTube educational patterns
        for pattern in YOUTUBE_EDU_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return VerificationMetadata(
                    status=VerificationStatus.VERIFIED,
                    platform="YouTube Education",
                    verification_method="whitelist",
                    verified_at=datetime.now()
                )

        return None

    async def analyze_educational_quality(
        self,
        content: str,
        metadata: Optional[Dict] = None
    ) -> EducationalAnalysis:
        """
        Use GPT-4 to analyze if content is educational and high-quality
        """
        try:
            # Prepare content sample (first 3000 characters)
            content_sample = content[:3000] if len(content) > 3000 else content

            # Build user prompt
            user_prompt = f"""Analyze this content for educational quality:

CONTENT TYPE: {metadata.get('source_type', 'unknown') if metadata else 'unknown'}
SOURCE: {metadata.get('source_identifier', 'unknown') if metadata else 'unknown'}

CONTENT SAMPLE (first 3000 characters):
{content_sample}

Provide your analysis in JSON format."""

            # Call GPT-4
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": EDUCATIONAL_CLASSIFIER_SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent classification
                response_format={"type": "json_object"}
            )

            # Parse response
            analysis_data = json.loads(response.choices[0].message.content)

            return EducationalAnalysis(**analysis_data)

        except Exception as e:
            # Fallback: return analysis based on error type
            print(f"⚠️ AI analysis failed: {str(e)}")

            # Check if it's a quota/billing error
            if "quota" in str(e).lower() or "429" in str(e):
                print("⚠️ OpenAI API quota exceeded - content will be unverified")
                return EducationalAnalysis(
                    is_educational=False,  # Will trigger REJECTED status
                    confidence=0.0,
                    topics=["API quota exceeded"],
                    educational_indicators=[],
                    non_educational_flags=["API quota exceeded"],
                    reasoning=f"OpenAI API quota exceeded. Please add credits at https://platform.openai.com/account/billing to enable content verification."
                )

            # For other errors, return cautious analysis that rejects
            return EducationalAnalysis(
                is_educational=False,
                confidence=0.0,
                topics=["Unknown"],
                educational_indicators=[],
                non_educational_flags=["AI analysis unavailable"],
                reasoning=f"AI analysis failed: {str(e)}. Cannot verify educational quality."
            )

    async def verify_content(
        self,
        content: str,
        url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> VerificationMetadata:
        """
        Main verification flow:
        1. Check whitelist (Tier 1)
        2. Check YouTube channel name from metadata
        3. AI analysis (Tier 2)
        4. Apply rejection criteria
        """
        # Step 1: Check whitelist
        whitelist_result = self.check_whitelist(url)
        if whitelist_result:
            print(f"✓ Content verified via whitelist: {whitelist_result.platform}")
            return whitelist_result

        # Step 2: Check if YouTube video is from known educational channel (using metadata)
        if metadata and metadata.get('title'):
            title = metadata.get('title', '')
            # Check if any known educational channel name is in the title metadata
            # (YouTube often includes channel name in video title metadata)
            for channel in YOUTUBE_EDU_CHANNELS:
                if channel.lower() in title.lower():
                    print(f"✓ Content verified via YouTube channel detection: {channel}")
                    return VerificationMetadata(
                        status=VerificationStatus.VERIFIED,
                        platform=f"YouTube - {channel}",
                        verification_method="youtube_channel_whitelist",
                        verified_at=datetime.now()
                    )

        # Step 2: AI Analysis
        print(f"🤖 Running AI educational analysis...")
        analysis = await self.analyze_educational_quality(content, metadata)

        print(f"AI Analysis Result:")
        print(f"  - Is Educational: {analysis.is_educational}")
        print(f"  - Confidence: {analysis.confidence}%")
        print(f"  - Topics: {', '.join(analysis.topics)}")
        print(f"  - Reasoning: {analysis.reasoning}")

        # Step 3: Apply rejection criteria

        # FIRST: Check if rejection is due to API quota issues (check this BEFORE confidence threshold)
        if analysis.non_educational_flags and "API quota exceeded" in analysis.non_educational_flags:
            # Return rejection with quota info so main.py can handle it
            print(f"⚠️ Quota exceeded detected - marking for fallback to PENDING status")
            return VerificationMetadata(
                status=VerificationStatus.REJECTED,
                confidence_score=analysis.confidence,
                rejection_reason=f"OpenAI API quota exceeded: {analysis.reasoning}",
                verification_method="ai_analysis",
                verified_at=datetime.now()
            )

        # Reject if confidence too low
        if analysis.confidence < self.confidence_threshold:
            return VerificationMetadata(
                status=VerificationStatus.REJECTED,
                confidence_score=analysis.confidence,
                rejection_reason=f"Low confidence ({analysis.confidence:.1f}%). AI is not confident this is educational content. Minimum required: {self.confidence_threshold}%.",
                verification_method="ai_analysis",
                verified_at=datetime.now()
            )

        # Reject if not educational
        if not analysis.is_educational:

            # Regular rejection for non-educational content
            flags = ', '.join(analysis.non_educational_flags) if analysis.non_educational_flags else "content does not meet educational criteria"
            return VerificationMetadata(
                status=VerificationStatus.REJECTED,
                confidence_score=analysis.confidence,
                rejection_reason=f"Non-educational content detected: {flags}",
                verification_method="ai_analysis",
                verified_at=datetime.now()
            )

        # Step 4: Accept as AI-verified
        print(f"✓ Content verified via AI analysis")
        return VerificationMetadata(
            status=VerificationStatus.AI_VERIFIED,
            confidence_score=analysis.confidence,
            verification_method="ai_analysis",
            verified_at=datetime.now()
        )
