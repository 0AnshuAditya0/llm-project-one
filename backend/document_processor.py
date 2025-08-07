import requests
import PyPDF2
import docx
from io import BytesIO
from typing import Dict, List, Optional
import re

class AdvancedDocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def process_document(self, url: str) -> Dict:
        """Process document from URL and extract text"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            
            if 'pdf' in content_type or url.endswith('.pdf'):
                text = self._extract_pdf_text(response.content)
            elif 'word' in content_type or url.endswith('.docx'):
                text = self._extract_docx_text(response.content)
            else:
                text = response.text
            
            return {
                'text': text,
                'metadata': self._extract_metadata(text),
                'document_type': self._detect_document_type(text),
                'url': url
            }
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        pdf_file = BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX"""
        doc_file = BytesIO(content)
        doc = docx.Document(doc_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_metadata(self, text: str) -> Dict:
        """Extract metadata from document"""
        return {
            'word_count': len(text.split()),
            'character_count': len(text),
            'paragraph_count': len(text.split('\n\n')),
            'has_tables': 'table' in text.lower(),
            'has_sections': bool(re.search(r'\b(section|clause|article)\s+\d+', text.lower()))
        }
    
    def _detect_document_type(self, text: str) -> str:
        """Detect document type based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['policy', 'insurance', 'premium', 'coverage']):
            return 'insurance_policy'
        elif any(word in text_lower for word in ['contract', 'agreement', 'terms']):
            return 'legal_contract'
        elif any(word in text_lower for word in ['employee', 'hr', 'benefits', 'salary']):
            return 'hr_document'
        else:
            return 'general_document'