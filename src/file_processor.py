"""
File processing utilities for handling LaTeX and PDF files.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import tempfile

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


class FileProcessor:
    """Handles processing of LaTeX and PDF files for paper evaluation."""
    
    @staticmethod
    def extract_title_from_latex(latex_content: str) -> Optional[str]:
        """Extract title from LaTeX content."""
        # Look for \title{...} command
        title_match = re.search(r'\\title\{([^}]+)\}', latex_content)
        if title_match:
            title = title_match.group(1)
            # Clean up LaTeX commands from title
            title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
            title = re.sub(r'\\[a-zA-Z]+', '', title)
            return title.strip()
        return None
    
    @staticmethod
    def extract_title_from_pdf(pdf_path: str) -> Optional[str]:
        """Extract title from PDF metadata or first page."""
        if not PyPDF2:
            return None
            
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Try to get title from metadata
                if reader.metadata and reader.metadata.get('/Title'):
                    return str(reader.metadata['/Title']).strip()
                
                # Try to extract from first page (basic heuristic)
                if len(reader.pages) > 0:
                    first_page = reader.pages[0].extract_text()
                    lines = first_page.split('\n')
                    # Look for a title-like line (often the first substantial line)
                    for line in lines[:10]:  # Check first 10 lines
                        line = line.strip()
                        if len(line) > 10 and len(line) < 200:  # Reasonable title length
                            return line
                            
        except Exception:
            pass
            
        return None
    
    @staticmethod
    def read_latex_file(file_path: str) -> Tuple[str, str]:
        """
        Read LaTeX file and extract content and title.
        
        Returns:
            Tuple of (content, title)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = FileProcessor.extract_title_from_latex(content) or "Unknown Paper"
        return content, title
    
    @staticmethod
    def read_pdf_file(file_path: str) -> Tuple[str, str]:
        """
        Read PDF file and extract content and title.
        
        Returns:
            Tuple of (content, title)
        """
        if not PyPDF2:
            raise ImportError("PyPDF2 is required to process PDF files. Install with: uv add PyPDF2")
        
        content_parts = []
        title = None
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract title
                title = FileProcessor.extract_title_from_pdf(file_path)
                
                # Extract text from all pages
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text.strip():
                        content_parts.append(page_text)
                        
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
        
        content = '\n\n'.join(content_parts)
        title = title or "Unknown Paper"
        
        return content, title
    
    @staticmethod
    def process_file(file_path: str) -> Tuple[str, str]:
        """
        Process a file (LaTeX or PDF) and extract content and title.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (content, title)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.tex':
            return FileProcessor.read_latex_file(file_path)
        elif file_extension == '.pdf':
            return FileProcessor.read_pdf_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported types: .tex, .pdf")
    
    @staticmethod
    def clean_text_for_evaluation(text: str) -> str:
        """Clean and prepare text for LLM evaluation."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove LaTeX commands that don't contribute to meaning
        text = re.sub(r'\\[a-zA-Z]+\*?\[[^\]]*\]', '', text)  # Commands with optional args
        text = re.sub(r'\\(begin|end)\{[^}]*\}', '', text)    # Environment markers
        text = re.sub(r'\\[a-zA-Z]+\*?', ' ', text)          # Simple commands
        
        # Clean up remaining artifacts
        text = re.sub(r'\{([^}]*)\}', r'\1', text)           # Remove braces
        text = re.sub(r'[\{\}]', '', text)                   # Remove remaining braces
        
        return text.strip()