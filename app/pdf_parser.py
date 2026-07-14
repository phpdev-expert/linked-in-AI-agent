"""Extract raw text from a LinkedIn 'Save to PDF' export and split into sections.

Pure module: no network, no LLM. Given PDF bytes, returns ProfileSections.
"""

import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.models import ProfileSections

# LinkedIn PDF section headings mapped to ProfileSections fields.
# "Summary" is LinkedIn's heading for the About section.
_HEADINGS = {
    "summary": "about",
    "about": "about",
    "experience": "experience",
    "education": "education",
    "skills": "skills",
}


def _extract_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except (PdfReadError, OSError, ValueError) as exc:
        raise ValueError("Could not read PDF") from exc
    if not reader.pages:
        raise ValueError("Could not read PDF")
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse(pdf_bytes: bytes) -> ProfileSections:
    """Parse PDF bytes into named profile sections.

    The text before the first recognized heading is treated as the
    name/headline block. Unrecognized lines are appended to the current
    section. Missing sections come back as empty strings.
    """
    text = _extract_text(pdf_bytes)

    buckets: dict[str, list[str]] = {
        "headline": [],
        "about": [],
        "experience": [],
        "education": [],
        "skills": [],
    }
    current = "headline"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key = _HEADINGS.get(line.lower())
        if key is not None:
            current = key
            continue  # drop the heading itself
        buckets[current].append(line)

    return ProfileSections(
        headline="\n".join(buckets["headline"]),
        about="\n".join(buckets["about"]),
        experience="\n".join(buckets["experience"]),
        education="\n".join(buckets["education"]),
        skills="\n".join(buckets["skills"]),
    )
