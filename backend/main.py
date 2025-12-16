from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import os
from dotenv import load_dotenv

from services.document_processor import DocumentProcessor
from services.quiz_generator import QuizGenerator
from services.video_processor import VideoProcessor
from services.verification_service import VerificationService
from models.quiz import QuizResponse
from models.verification import VerificationStatus, SourceInfo

load_dotenv()

app = FastAPI(title="Quiz Generator API")

# Configure CORS for both development and production
allowed_origins = [
    "http://localhost:3000",  # Local development
    "https://*.vercel.app",   # Vercel preview deployments
]

# Add production URL from environment variable if set
production_url = os.getenv("FRONTEND_URL")
if production_url:
    allowed_origins.append(production_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
openai_api_key = os.getenv("OPENAI_API_KEY")
document_processor = DocumentProcessor(openai_api_key=openai_api_key)
quiz_generator = QuizGenerator()

# Initialize video and verification services if OpenAI key available
video_processor = VideoProcessor(openai_api_key) if openai_api_key else None
verification_service = VerificationService(openai_api_key) if openai_api_key else None


@app.get("/")
async def root():
    return {"message": "Quiz Generator API is running"}


@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None)
):
    """
    Generate a quiz from:
    - Uploaded file (PDF, DOCX, TXT, video files)
    - Web URL
    - Video URL (YouTube, Vimeo, any platform)

    Includes educational content verification and points calculation
    """
    if not file and not url and not video_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide a file, URL, or video URL"
        )

    content = None
    source_info = None

    try:
        # Route 1: Video URL
        if video_url:
            if not video_processor:
                raise HTTPException(
                    status_code=500,
                    detail="Video processing unavailable. OpenAI API key not configured."
                )

            print(f"📹 Processing video URL: {video_url}")
            result = await video_processor.process_video_url(video_url)
            content = result.transcript
            source_info = SourceInfo(
                source_type="video_url",
                source_identifier=video_url,
                title=result.title,
                duration=result.duration,
                transcript_length=len(content)
            )

        # Route 2: File Upload (including video files)
        elif file:
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
                print(f"📹 Processing video file: {file.filename}")
                source_type = "video_file"
            else:
                print(f"📄 Processing document file: {file.filename}")
                source_type = "document_file"

            content = await document_processor.process_file(file)
            source_info = SourceInfo(
                source_type=source_type,
                source_identifier=file.filename,
                transcript_length=len(content) if source_type == "video_file" else None
            )

        # Route 3: Web URL
        elif url:
            print(f"🌐 Processing web URL: {url}")
            content = await document_processor.process_url(url)
            source_info = SourceInfo(
                source_type="web_url",
                source_identifier=url
            )

        # Validate content length
        if not content or len(content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="The provided content is too short to generate a quiz"
            )

        # Verify educational quality (if verification service available)
        verification = None
        if verification_service:
            print(f"🔍 Verifying educational content...")
            verification = await verification_service.verify_content(
                content=content,
                url=video_url or url,
                metadata=source_info.dict() if source_info else None
            )

            # Reject if failed verification (but not if quota exceeded)
            if verification.status == VerificationStatus.REJECTED:
                # Check if rejection is due to API quota
                if verification.rejection_reason and "quota" in verification.rejection_reason.lower():
                    # Allow content to pass as unverified when quota exceeded
                    print(f"⚠️ API quota exceeded - allowing content as unverified")
                    from models.verification import VerificationMetadata
                    from datetime import datetime
                    verification = VerificationMetadata(
                        status=VerificationStatus.PENDING,
                        verification_method="api_unavailable",
                        verified_at=datetime.now()
                    )
                else:
                    # Reject for actual educational quality issues
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "error": "Content Rejected",
                            "reason": verification.rejection_reason,
                            "confidence": verification.confidence_score
                        }
                    )

        # Generate quiz
        print(f"🎯 Generating quiz...")
        quiz_data = await quiz_generator.generate_quiz(content)

        # Calculate points based on verification status
        if verification:
            if verification.status == VerificationStatus.VERIFIED:
                points_awarded = 150  # Verified platforms
            elif verification.status == VerificationStatus.AI_VERIFIED:
                points_awarded = 100  # AI-verified content
            else:
                points_awarded = 50   # Fallback
        else:
            points_awarded = 50  # No verification available

        # Attach metadata to response
        quiz_data.verification = verification
        quiz_data.source_info = source_info
        quiz_data.points_awarded = points_awarded

        print(f"✅ Quiz generated successfully!")
        return quiz_data

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
