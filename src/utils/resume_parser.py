import io
from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    @staticmethod
    def extract_text(file_obj) -> str:
        try:
            if not file_obj:
                return ""
            
            reader = PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
            clean_text = text.strip()
            logger.info(f"Extracted {len(clean_text)} chars from resume")
            return clean_text
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return ""