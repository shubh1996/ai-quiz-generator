from fastapi import UploadFile
import PyPDF2
from docx import Document
from bs4 import BeautifulSoup
import requests
import io


class DocumentProcessor:
    """
    Processes documents and URLs to extract text content
    """

    async def process_file(self, file: UploadFile) -> str:
        """
        Extract text from uploaded file (PDF, TXT, DOCX)
        """
        content = await file.read()
        file_extension = file.filename.split('.')[-1].lower()

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
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                element.decompose()

            # Try to extract main content first
            main_content = soup.find('main') or soup.find('article') or soup.find(class_='content') or soup

            text = main_content.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = ' '.join(text.split())

            return text

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
