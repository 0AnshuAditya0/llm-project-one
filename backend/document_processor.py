import requests
import PyPDF2
from io import BytesIO
import re
from typing import List

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    def download_and_process_pdf(self, blob_url: str) -> str:
        """Download PDF from URL and extract text"""
        try:
            print(f"Downloading PDF from: {blob_url}")
            response = requests.get(blob_url, timeout=30)
            response.raise_for_status()
            
            # Read PDF content
            pdf_file = BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            print(f"Successfully extracted {len(text)} characters from PDF")
            return self.clean_text(text)
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def chunk_document(self, text: str) -> List[str]:
        """Split document into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence ending within last 100 characters
                last_period = text.rfind('.', start, end)
                if last_period > start + self.chunk_size - 100:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        print(f"Created {len(chunks)} document chunks")
        return chunks