from docx import Document
from .skills_library import SKILLS
from .roles_library import ROLES

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

def extract_skills(text):
    """
    Extract matching skills from resume text.
    """
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return sorted(set(found_skills))

def extract_experience_years(text):
    """
    Extract years of experience from resume text.
    """
    patterns = [
        r"(\d+)\+?\s+years?\s+of\s+experience",
        r"experience\s*:\s*(\d+)\+?\s+years?",
        r"(\d+)\+?\s+yrs?",
    ]

    text = text.lower()

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return int(match.group(1))

    return None

def extract_roles(text):
    """
    Extract job roles from resume text.
    """
    text = text.lower()

    found_roles = []

    for role in ROLES:
        pattern = r"\b" + re.escape(role.lower()) + r"\b"

        if re.search(pattern, text):
            found_roles.append(role)

    return sorted(set(found_roles))

def extract_education(text):
    """
    Extract education qualifications from resume text.
    """
    qualifications = [
        "b.tech",
        "b.e",
        "bachelor of technology",
        "bachelor of engineering",
        "b.sc",
        "bachelor of science",
        "bca",
        "m.tech",
        "m.e",
        "master of technology",
        "master of engineering",
        "m.sc",
        "master of science",
        "mca",
        "phd",
        "doctorate",
        "diploma",
        "higher secondary",
        "12th",
        "10th",
    ]

    text = text.lower()

    found = []

    for qualification in qualifications:
        pattern = r"\b" + re.escape(qualification) + r"\b"

        if re.search(pattern, text):
            found.append(qualification)

    return sorted(set(found))

def parse_resume(file_path):
    """
    Parse a resume into structured data.
    """
    text = extract_resume_text(file_path)

    return {
        "raw_text": text,
        "skills": extract_skills(text),
        "roles": extract_roles(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text),
    }