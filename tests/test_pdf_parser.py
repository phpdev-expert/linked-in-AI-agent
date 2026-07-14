from pathlib import Path

from app.models import ProfileSections
from app.pdf_parser import parse

FIXTURE = Path(__file__).parent / "fixtures" / "sample_profile.pdf"


def test_parse_returns_profile_sections():
    result = parse(FIXTURE.read_bytes())
    assert isinstance(result, ProfileSections)


def test_parse_extracts_headline_from_top_block():
    result = parse(FIXTURE.read_bytes())
    assert "Jane Developer" in result.headline
    assert "Senior Backend Engineer" in result.headline


def test_parse_extracts_named_sections():
    result = parse(FIXTURE.read_bytes())
    assert "reliable APIs" in result.about
    assert "millions of requests" in result.experience
    assert "State University" in result.education
    assert "FastAPI" in result.skills


def test_parse_missing_section_is_empty_not_error():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(72, 750, "Only A Name")
    c.save()
    result = parse(buf.getvalue())
    assert result.about == ""
    assert result.experience == ""


def test_parse_rejects_non_pdf():
    import pytest

    with pytest.raises(ValueError):
        parse(b"this is not a pdf")
