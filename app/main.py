"""FastAPI app: serves the upload page and handles analysis requests.

The analyze function is provided via a dependency so tests can override it and
avoid real Claude calls.
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import analyzer, pdf_parser
from app.models import Report

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

app = FastAPI(title="LinkedIn Profile Optimizer")


def get_analyze_fn():
    """Return a function(sections) -> Report using a real Anthropic client.

    Overridden in tests. Imported here (not at module load) so the app starts
    without an API key until an analysis is actually requested.
    """
    from anthropic import Anthropic

    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    def _run(sections) -> Report:
        return analyzer.analyze(sections, client=client, model=DEFAULT_MODEL)

    return _run


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return TEMPLATES.TemplateResponse(request, "upload.html", {"error": None})


@app.post("/analyze", response_class=HTMLResponse)
def analyze_profile(
    request: Request,
    file: UploadFile = File(...),
    analyze_fn=Depends(get_analyze_fn),
):
    pdf_bytes = file.file.read()
    try:
        sections = pdf_parser.parse(pdf_bytes)
    except ValueError:
        return TEMPLATES.TemplateResponse(
            request,
            "upload.html",
            {"error": "That doesn't look like a readable PDF. Re-export from LinkedIn and try again."},
            status_code=400,
        )

    if not any(
        [sections.headline, sections.about, sections.experience, sections.education, sections.skills]
    ):
        return TEMPLATES.TemplateResponse(
            request,
            "upload.html",
            {"error": "No text found in that PDF. Use LinkedIn's 'Save to PDF' export."},
            status_code=400,
        )

    try:
        report = analyze_fn(sections)
    except ValueError:
        return TEMPLATES.TemplateResponse(
            request,
            "upload.html",
            {"error": "The analysis failed to complete. Please try again."},
            status_code=502,
        )

    return TEMPLATES.TemplateResponse(request, "report.html", {"report": report})
