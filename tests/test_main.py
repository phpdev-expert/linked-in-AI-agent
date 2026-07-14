from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, get_analyze_fn
from app.models import Report, SectionResult

FIXTURE = Path(__file__).parent / "fixtures" / "sample_profile.pdf"


def _fake_analyze(sections):
    return Report(
        overall_score=88,
        sections=[SectionResult(name="Headline", score=90, critique="Great.", rewrite="Rewritten headline.")],
        keywords=["python", "fastapi"],
    )


def setup_function():
    app.dependency_overrides[get_analyze_fn] = lambda: _fake_analyze


def teardown_function():
    app.dependency_overrides.clear()


def test_get_root_shows_upload_form():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Save to PDF" in resp.text
    assert "<form" in resp.text


def test_post_analyze_renders_report():
    client = TestClient(app)
    with FIXTURE.open("rb") as f:
        resp = client.post("/analyze", files={"file": ("profile.pdf", f, "application/pdf")})
    assert resp.status_code == 200
    assert "88/100" in resp.text
    assert "Rewritten headline." in resp.text
    assert "python" in resp.text


def test_post_analyze_rejects_non_pdf():
    client = TestClient(app)
    resp = client.post("/analyze", files={"file": ("note.txt", b"hello", "text/plain")})
    assert resp.status_code == 400
    assert "PDF" in resp.text
