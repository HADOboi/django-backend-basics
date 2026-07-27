from docx import Document

import os, re, logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_pdf_text(file_path):
    """
    Extract text from a PDF file.
    """
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text

def extract_docx_text(file_path):
    """
    Extract text from a DOCX file.
    """
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text

def extract_resume_text(file_path):
    """
    Extract text from a resume based on its file type.
    """

    try:
        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            text = extract_pdf_text(file_path)

        elif extension == ".docx":
            text = extract_docx_text(file_path)

        else:
            raise ValueError("Unsupported file format")

        return clean_resume_text(text)
    
    except Exception as e:
        logger.exception("Resume parsing failed")
        raise ValueError(f"Failed to parse resume: {e}")

def clean_resume_text(text):
    """
    Clean and normalize extracted resume text.
    """

    # Replace multiple whitespace with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E]", " ", text)

    # Remove extra spaces
    text = text.strip()

    return text