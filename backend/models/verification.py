from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from datetime import datetime


class VerificationStatus(str, Enum):
    """Status of content verification"""
    VERIFIED = "verified"          # Tier 1: Known educational platform
    AI_VERIFIED = "ai_verified"    # Tier 2: AI validated as educational
    REJECTED = "rejected"          # Failed verification
    PENDING = "pending"            # Processing


class VerificationMetadata(BaseModel):
    """Metadata about content verification"""
    status: VerificationStatus
    confidence_score: Optional[float] = None  # AI confidence (0-100)
    platform: Optional[str] = None            # YouTube, Coursera, etc.
    rejection_reason: Optional[str] = None    # Why it was rejected
    verified_at: datetime
    verification_method: str                  # "whitelist" or "ai_analysis"


class EducationalAnalysis(BaseModel):
    """Result of AI educational content analysis"""
    is_educational: bool
    confidence: float                         # 0-100
    topics: List[str]
    educational_indicators: List[str]         # What makes it educational
    non_educational_flags: List[str]          # Red flags found
    reasoning: str                            # AI explanation


class SourceInfo(BaseModel):
    """Information about the content source"""
    source_type: str                          # "video_url", "video_file", "pdf", "url", "document"
    source_identifier: str                    # URL or filename
    title: Optional[str] = None              # Extracted video/page title
    duration: Optional[int] = None           # For videos (seconds)
    transcript_length: Optional[int] = None  # Character count
