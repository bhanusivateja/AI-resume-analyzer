"""
resume_parser.py - Robust PDF Extraction and Resume Section Parsing
Extracts raw text, contact information, education, experience, projects, and certifications.
"""

import io
import re
from typing import Dict, Any, Optional, List, Tuple
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


class ResumeParsingError(Exception):
    """Custom exception raised when resume parsing fails."""
    pass


class ResumeParser:
    """Handles PDF validation, text extraction, contact extraction, and section segmenting."""

    MAX_FILE_SIZE_MB = 10.0

    # Common section header patterns
    SECTION_PATTERNS = {
        "summary": r"(?:summary|professional\s+summary|profile|about\s+me|career\s+objective|objective)",
        "skills": r"(?:technical\s+skills|core\s+skills|skills|technologies|proficiencies|competencies|tools\s+&\s+technologies)",
        "experience": r"(?:work\s+experience|professional\s+experience|experience|employment\s+history|internships|work\s+history)",
        "education": r"(?:education|academic\s+background|qualifications|academic\s+qualifications|educational\s+details)",
        "projects": r"(?:projects|academic\s+projects|technical\s+projects|key\s+projects|personal\s+projects)",
        "certifications": r"(?:certifications|certificates|licenses|achievements|honors|publications|awards)",
    }

    DEGREE_PATTERNS = [
        r"\b(?:b\.?tech|b\.?e\.?|bachelor(?:\s+of\s+engineering|\s+of\s+technology|\s+of\s+science|\s+of\s+arts)?|b\.?s\.?|b\.?sc)\b",
        r"\b(?:m\.?tech|m\.?e\.?|master(?:\s+of\s+engineering|\s+of\s+technology|\s+of\s+science|\s+of\s+business\s+administration)?|m\.?s\.?|m\.?sc|m\.?b\.?a)\b",
        r"\b(?:ph\.?d|doctor\s+of\s+philosophy|doctorate)\b",
        r"\b(?:diploma|associate(?:\s+degree)?)\b"
    ]

    def __init__(self):
        pass

    def validate_file(self, file_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """Validate file format, size, and readability."""
        if not filename.lower().endswith(".pdf"):
            return False, "Invalid file format. Only PDF files are supported."

        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed size of {self.MAX_FILE_SIZE_MB} MB."

        if len(file_bytes) == 0:
            return False, "The uploaded file is empty (0 bytes)."

        return True, None

    def extract_text_from_pdf(self, file_source: Any) -> Tuple[str, int]:
        """
        Extract raw text and page count from PDF stream or bytes.
        Returns (extracted_text, page_count).
        """
        try:
            if isinstance(file_source, bytes):
                pdf_stream = io.BytesIO(file_source)
            elif hasattr(file_source, "read"):
                # File-like object (e.g. Streamlit UploadedFile)
                content = file_source.read()
                pdf_stream = io.BytesIO(content)
                # Reset pointer if needed
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
            else:
                with open(file_source, "rb") as f:
                    pdf_stream = io.BytesIO(f.read())

            # Count pages safely
            pdf_stream.seek(0)
            try:
                page_count = sum(1 for _ in PDFPage.get_pages(pdf_stream))
            except Exception:
                page_count = 1

            pdf_stream.seek(0)
            laparams = LAParams(line_margin=0.3, word_margin=0.1)
            raw_text = extract_text(pdf_stream, laparams=laparams)

            if not raw_text or not raw_text.strip():
                raise ResumeParsingError(
                    "No extractable text was found in the PDF. The file might be a scanned image or protected."
                )

            return raw_text, page_count

        except ResumeParsingError:
            raise
        except Exception as e:
            raise ResumeParsingError(f"Error reading PDF content: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted resume text."""
        if not text:
            return ""

        # Replace non-breaking spaces and irregular characters
        text = text.replace("\xa0", " ").replace("\u200b", " ")
        # Replace carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace bullets with standard hyphens
        text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25CF]", "\n- ", text)
        # Collapse multiple horizontal spaces
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines (more than 2 to 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract candidate email, phone, links, and name."""
        contacts: Dict[str, Optional[str]] = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "portfolio": None
        }

        # Email regex
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            contacts["email"] = email_match.group(0).strip()

        # Phone regex (international & local standards)
        phone_match = re.search(
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}",
            text
        )
        if phone_match:
            contacts["phone"] = phone_match.group(0).strip()

        # LinkedIn regex
        linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|profile)/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
        if linkedin_match:
            contacts["linkedin"] = linkedin_match.group(0).strip()

        # GitHub regex
        github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", text, re.IGNORECASE)
        if github_match:
            contacts["github"] = github_match.group(0).strip()

        # Portfolio / Personal Website
        portfolio_match = re.search(
            r"(?:https?://)?(?:www\.)?(?!linkedin|github)[a-zA-Z0-9-]+\.(?:github\.io|vercel\.app|netlify\.app|dev|me|io|com|org)",
            text,
            re.IGNORECASE
        )
        if portfolio_match:
            contacts["portfolio"] = portfolio_match.group(0).strip()

        # Name heuristic: inspect first 5 non-empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Filter out lines that look like emails, urls, or resume header titles
            if (
                "@" not in line
                and not re.search(r"(?:curriculum\s+vitae|resume|phone|email|linkedin|github|contact)", line, re.IGNORECASE)
                and len(line.split()) in range(1, 5)
                and re.match(r"^[A-Za-z\s.'-]+$", line)
            ):
                contacts["name"] = line
                break

        return contacts

    def segment_sections(self, text: str) -> Dict[str, str]:
        """
        Segment the resume into standard sections:
        summary, skills, experience, education, projects, certifications.
        """
        sections: Dict[str, str] = {
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": "",
            "certifications": "",
            "other": ""
        }

        # Build regex for headings
        heading_keys = list(self.SECTION_PATTERNS.keys())
        combined_pattern = "|".join(
            f"(?P<{k}>^[ \\t]*{self.SECTION_PATTERNS[k]}\\b[ \\t]*(?::)?)"
            for k in heading_keys
        )

        lines = text.split("\n")
        current_section = "other"
        section_lines: Dict[str, List[str]] = {k: [] for k in sections.keys()}

        for line in lines:
            trimmed = line.strip()
            # Check if this line is a heading
            match = re.match(combined_pattern, trimmed, re.IGNORECASE)
            if match and len(trimmed) < 45:
                # Identified a section header
                for sec_name in heading_keys:
                    if match.group(sec_name):
                        current_section = sec_name
                        break
            else:
                section_lines[current_section].append(line)

        for sec in sections.keys():
            sections[sec] = "\n".join(section_lines[sec]).strip()

        return sections

    def extract_education_details(self, education_text: str) -> List[Dict[str, str]]:
        """Extract degrees, institutions, and graduation years from education section."""
        details = []
        if not education_text:
            return details

        lines = [line.strip() for line in education_text.split("\n") if line.strip()]
        year_pattern = r"\b(?:19|20)\d{2}\b"

        for line in lines:
            degree_found = None
            for deg_pat in self.DEGREE_PATTERNS:
                deg_match = re.search(deg_pat, line, re.IGNORECASE)
                if deg_match:
                    degree_found = deg_match.group(0).upper()
                    break

            year_match = re.search(year_pattern, line)
            year = year_match.group(0) if year_match else None

            if degree_found or year or len(line) > 15:
                details.append({
                    "entry": line,
                    "degree": degree_found,
                    "year": year
                })

        return details

    def parse(self, file_source: Any, filename: str = "resume.pdf") -> Dict[str, Any]:
        """
        Complete parsing pipeline: validation, text extraction, contact info,
        section segmentation, and metadata computation.
        """
        # Read bytes if needed for validation
        if hasattr(file_source, "read"):
            content = file_source.read()
            if hasattr(file_source, "seek"):
                file_source.seek(0)
        elif isinstance(file_source, bytes):
            content = file_source
        else:
            with open(file_source, "rb") as f:
                content = f.read()

        # Validate
        valid, err = self.validate_file(content, filename)
        if not valid:
            raise ResumeParsingError(err)

        # Extract text & pages
        raw_text, page_count = self.extract_text_from_pdf(content)
        cleaned_text = self.clean_text(raw_text)

        # Contacts & Sections
        contacts = self.extract_contact_info(cleaned_text)
        sections = self.segment_sections(cleaned_text)
        edu_details = self.extract_education_details(sections.get("education", ""))

        words = cleaned_text.split()
        word_count = len(words)
        char_count = len(cleaned_text)
        reading_time_minutes = round(word_count / 200, 1)

        return {
            "filename": filename,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "contact_info": contacts,
            "sections": sections,
            "education_details": edu_details,
            "metadata": {
                "page_count": page_count,
                "word_count": word_count,
                "char_count": char_count,
                "reading_time_minutes": reading_time_minutes
            }
        }
