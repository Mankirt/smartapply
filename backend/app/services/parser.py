import re
import logging
import pdfplumber
from io import BytesIO
from app.models.schemas import ResumeSection

logger = logging.getLogger(__name__)

SECTION_PATTERNS = {
    r"(work\s*)?experience|employment|professional": "experience",
    r"technical\s*skills?|skills?|technologies|competencies": "skills",
    r"education|academic|degrees?": "education",
    r"projects?|personal\s*projects?": "projects",
    r"summary|objective|profile": "summary",
    r"certifications?|licenses?": "certifications",
}


def detect_section_type(heading: str) -> str:
    heading_lower = heading.lower().strip()
    for pattern, section_type in SECTION_PATTERNS.items():
        if re.search(pattern, heading_lower):
            return section_type
    return "other"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def split_into_sections(text: str) -> list[tuple[str, str]]:
    lines = text.split("\n")
    sections = []
    current_heading = "Header"
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        is_heading = (
            len(stripped) < 60
            and (stripped.isupper() or stripped.istitle())
            and detect_section_type(stripped) != "other"
        )

        if is_heading:
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = stripped
            current_lines = []
        else:
            current_lines.append(line)

    # Save the last section — loop only saves when it hits a NEW heading
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines).strip()))

    return sections


async def parse_pdf_to_sections(pdf_bytes: bytes) -> list[ResumeSection]:
    raw_text = extract_text_from_pdf(pdf_bytes)

    if not raw_text.strip():
        raise ValueError("PDF appears to be empty or image-based (no extractable text)")

    raw_sections = split_into_sections(raw_text)
    logger.info(f"Parsed {len(raw_sections)} sections from resume")

    sections = []
    for i, (heading, content) in enumerate(raw_sections):
        if not content.strip():
            continue
        sections.append(
            ResumeSection(
                section_type=detect_section_type(heading),
                title=heading,
                content=content,
                order=i,
            )
        )

    return sections