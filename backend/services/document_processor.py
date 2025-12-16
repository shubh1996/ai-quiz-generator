from fastapi import UploadFile
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import requests
import io
import os
import tempfile
from openai import AsyncOpenAI


class DocumentProcessor:
    """
    Processes documents and URLs to extract text content
    """

    def __init__(self, openai_api_key: str = None):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

    async def process_file(self, file: UploadFile) -> str:
        """
        Extract text from uploaded file (PDF, TXT, DOCX, video files)
        """
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()

        # Check if it's a video file
        if file_extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            return await self.process_video_file(file, content)

        if file_extension == 'pdf':
            return self._extract_from_pdf(content)
        elif file_extension == 'txt':
            return content.decode('utf-8')
        elif file_extension in ['doc', 'docx']:
            return self._extract_from_docx(content)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    async def process_url(self, url: str) -> str:
        """
        Extract text content from a URL
        """
        try:
            # Add proper headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            print(f"📡 Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            print(f"✓ Successfully fetched URL (status {response.status_code})")

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                element.decompose()

            # Try to extract main content with multiple strategies
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find(class_='content') or
                soup.find(class_='article') or
                soup.find(class_='post-content') or
                soup.find(id='content') or
                soup.find(id='main') or
                soup.find('body') or
                soup
            )

            text = main_content.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = ' '.join(text.split())

            if len(text) < 100:
                raise ValueError("Extracted text is too short. The page might not have loaded properly.")

            print(f"✓ Extracted {len(text)} characters from URL")
            return text

        except requests.exceptions.Timeout:
            raise ValueError(f"Request timed out. The URL took too long to respond.")
        except requests.exceptions.ConnectionError:
            raise ValueError(f"Could not connect to the URL. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"HTTP error {e.response.status_code}: {e.response.reason}")
        except Exception as e:
            raise ValueError(f"Failed to fetch content from URL: {str(e)}")

    def _extract_from_pdf(self, content: bytes) -> str:
        """
        Extract text from PDF file
        """
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def _extract_from_docx(self, content: bytes) -> str:
        """
        Extract text from DOCX file
        """
        try:
            doc_file = io.BytesIO(content)
            doc = Document(doc_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    async def process_video_file(self, file: UploadFile, content: bytes) -> str:
        """
        Process uploaded video file:
        1. Save to temporary location
        2. Extract audio
        3. Transcribe with Whisper API
        4. Return transcript
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key is required for video transcription")

        temp_video_path = None
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_video:
                temp_video.write(content)
                temp_video_path = temp_video.name

            # Extract audio using pydub (requires ffmpeg)
            from pydub import AudioSegment

            print(f"🎬 Processing video file: {file.filename}")
            audio = AudioSegment.from_file(temp_video_path)

            # Export as mp3
            temp_audio_path = temp_video_path.replace(temp_video_path.split('.')[-1], 'mp3')
            audio.export(temp_audio_path, format='mp3')
            print(f"🎵 Extracted audio to temporary file")

            # Transcribe with Whisper
            print(f"🎤 Transcribing audio...")
            with open(temp_audio_path, 'rb') as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )

            transcript_text = transcript if isinstance(transcript, str) else transcript.text
            print(f"✓ Transcription complete ({len(transcript_text)} characters)")

            # Cleanup
            os.remove(temp_video_path)
            os.remove(temp_audio_path)

            return transcript_text

        except ImportError:
            raise ValueError("pydub library is required for video processing. Please install it: pip install pydub")
        except Exception as e:
            # Cleanup on error
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            raise ValueError(f"Failed to process video file: {str(e)}")
