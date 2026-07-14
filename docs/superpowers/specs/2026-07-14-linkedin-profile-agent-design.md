# LinkedIn Profile Optimizer Agent — Design

**Date:** 2026-07-14
**Status:** Approved

## Purpose

An agent that audits a person's LinkedIn profile against general best practices
and returns an actionable report: an overall score, per-section scores and
critiques, ready-to-paste rewritten copy, and a suggested keyword list to
improve searchability.

No live LinkedIn integration. The user provides their profile via LinkedIn's
"Save to PDF" export. This avoids LinkedIn API restrictions and ToS issues
around scraping.

## Scope

**In scope**
- Upload a LinkedIn "Save to PDF" export via a local web UI.
- Parse the PDF into named sections.
- One structured Claude call that scores, critiques, rewrites, and suggests keywords.
- Render an HTML report with copy-to-clipboard rewrites.

**Out of scope (YAGNI)**
- Live LinkedIn API / scraping.
- Tailoring toward a specific target job (general best-practices only).
- Authentication, user accounts, persistence, deployment. Local dev only.
- Writing changes back to LinkedIn.

## Architecture

Fixed pipeline (chosen over an agentic loop because the workflow is fully
determined): **parse → analyze → render**.

```
Browser (upload page)
    │  POST /analyze  (multipart PDF)
    ▼
FastAPI (main.py)
    │
    ├─ pdf_parser.py   bytes ──► { headline, about, experience, education, skills }
    │
    ├─ analyzer.py     sections ──► Claude (single structured call) ──► Report
    │
    └─ render report page  ◄── Report
```

### Modules

Each module has one purpose, a clear interface, and is independently testable.

- **`models.py`** — Pydantic schemas.
  - `ProfileSections`: parsed profile text by section.
  - `SectionResult`: `{ name, score: int, critique: str, rewrite: str }`.
  - `Report`: `{ overall_score: int, sections: list[SectionResult], keywords: list[str] }`.
  - The `Report` schema doubles as the JSON contract Claude must return.

- **`pdf_parser.py`** — `parse(pdf_bytes) -> ProfileSections`.
  - Pure, no network. Uses `pypdf` to extract text, then segments by known
    LinkedIn PDF headings (Summary/About, Experience, Education, Skills, plus
    the top-of-document name/headline block).
  - Missing sections come back empty rather than raising.

- **`analyzer.py`** — `analyze(sections, client) -> Report`.
  - Builds a structured prompt embedding each section and the scoring rubric.
  - Calls Claude (default model `claude-sonnet-4-6`) requesting JSON matching
    the `Report` schema.
  - The Anthropic client is injected so tests pass a mock. Validates the
    response against the Pydantic schema.

- **`main.py`** — FastAPI app.
  - `GET /` → upload page.
  - `POST /analyze` → parse + analyze + render report page.
  - Constructs the real Anthropic client from `ANTHROPIC_API_KEY`.

- **`templates/`** — `upload.html` (file input) and `report.html` (overall
  score, per-section cards with score + critique + copy-to-clipboard rewrite,
  keyword list). Minimal vanilla JS; no build step.

## Data flow

1. User opens `/`, selects their LinkedIn PDF export, submits.
2. `POST /analyze` receives the multipart file.
3. `pdf_parser.parse` → `ProfileSections`.
4. `analyzer.analyze` → single Claude call → validated `Report`.
5. `report.html` rendered with the `Report`.

## Scoring rubric (best-practices, given to Claude)

- **Headline** — beyond just job title; value/specialty; keyword-rich.
- **About** — hook in first lines; first person; quantified impact; clear CTA.
- **Experience** — achievement-oriented bullets with metrics, not duties.
- **Skills/Keywords** — coverage of relevant industry terms for searchability.
- **Completeness** — presence and depth of each section.

Scores are 0–100 per section and an overall 0–100.

## Error handling

- Non-PDF or unreadable upload → 400 with a clear message on the page.
- Empty extracted text → message asking the user to re-export the PDF.
- Missing individual sections → analyze what is present; note the gap.
- Malformed JSON from Claude → retry the call once; if it fails again, show a
  friendly error and ask the user to try again.

## Testing

- `pdf_parser`: unit tests against a small sample LinkedIn PDF export
  (fixture), asserting correct sectioning and graceful handling of a missing
  section.
- `analyzer`: unit tests with a **mocked** Anthropic client — assert the prompt
  contains each section and the rubric, and that a canned JSON response parses
  into a valid `Report`; assert the retry path on malformed JSON.
- `main`: one integration test hitting `POST /analyze` with a fixture PDF and a
  mocked analyzer/LLM, asserting the report page renders expected values.

## Tech choices

- **Language:** Python 3.11+
- **Web:** FastAPI + Uvicorn, Jinja2 templates, server-rendered (no SPA).
- **PDF:** `pypdf`.
- **LLM:** Anthropic SDK, default model `claude-sonnet-4-6`
  (model configurable via env var; Opus 4.8 available for higher quality).
- **Config:** `ANTHROPIC_API_KEY` from environment.
- **Deployment:** local dev only (`uvicorn`), no auth.
