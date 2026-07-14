# LinkedIn Profile Optimizer Agent

An AI agent that audits your LinkedIn profile against general best practices and
returns an actionable report: an overall score, per-section scores and
critiques, **ready-to-paste rewritten copy**, and a suggested keyword list to
improve how easily recruiters find you.

You give it your profile as a LinkedIn **"Save to PDF"** export — no LinkedIn
login, no API keys for LinkedIn, no scraping. The agent parses the PDF, sends
the sections to Claude in a single structured call, and renders a clean report
in your browser.

> Status: in active development. See
> [`docs/superpowers/specs/2026-07-14-linkedin-profile-agent-design.md`](docs/superpowers/specs/2026-07-14-linkedin-profile-agent-design.md)
> for the full design.

---

## Why PDF export instead of the LinkedIn API?

LinkedIn's profile-editing API is not available to most developers, and scraping
public profiles violates LinkedIn's Terms of Service and is fragile. Exporting
your own profile to PDF is fully within your rights, needs no authentication,
and works for everyone. LinkedIn provides this via
**Profile → Resources → Save to PDF**.

---

## Features

- **Overall profile score** (0–100) with a per-section breakdown.
- **Section-by-section critique** for Headline, About, Experience, Education,
  and Skills.
- **Ready-to-paste rewrites** of each section, with a copy-to-clipboard button.
- **Keyword suggestions** to improve search visibility for recruiters.
- **Local-first & private** — runs on your machine; your profile is only sent to
  the Anthropic API for analysis, never stored.

---

## How it works

A fixed, easy-to-reason-about pipeline: **parse → analyze → render**.

```
Browser (upload page)
    │  POST /analyze  (your LinkedIn PDF)
    ▼
FastAPI backend
    │
    ├─ pdf_parser   PDF bytes ─► { headline, about, experience, education, skills }
    │
    ├─ analyzer     sections  ─► Claude (one structured call) ─► Report
    │
    └─ render report page  ◄── Report (scores, critiques, rewrites, keywords)
```

### Scoring rubric

The agent scores your profile against these best practices:

| Section     | What "good" looks like                                                    |
|-------------|---------------------------------------------------------------------------|
| Headline    | More than a job title — states value/specialty, keyword-rich             |
| About       | Strong hook in the first lines, first person, quantified impact, clear CTA |
| Experience  | Achievement-oriented bullets with metrics, not a list of duties           |
| Skills      | Covers relevant industry terms so recruiter searches surface you          |
| Completeness| Every section present and with meaningful depth                           |

---

## Tech stack

- **Python 3.11+**
- **FastAPI** + **Uvicorn** — backend and local server
- **Jinja2** — server-rendered pages (no SPA, no build step)
- **pypdf** — PDF text extraction
- **Anthropic SDK** — Claude for the analysis
  (default model `claude-sonnet-4-6`, configurable)

---

## Getting started

> These steps describe the intended setup. Application code is being implemented
> against the approved design spec.

### 1. Clone and install

```bash
git clone https://github.com/phpdev-expert/linked-in-AI-agent.git
cd linked-in-AI-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your Anthropic API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# optional: override the default model
export ANTHROPIC_MODEL="claude-sonnet-4-6"
```

Get a key from the [Anthropic Console](https://console.anthropic.com/).

### 3. Run the app

```bash
uvicorn app.main:app --reload
```

Open <http://localhost:8000>, upload your LinkedIn PDF export, and view the
report.

---

## Usage

1. In LinkedIn, go to your profile → **Resources** → **Save to PDF**.
2. Open the app at <http://localhost:8000>.
3. Upload the downloaded PDF.
4. Review your scores, critiques, and rewrites — copy the rewritten sections
   straight into LinkedIn.

---

## Project layout

```
app/
  main.py          FastAPI routes; serves the pages
  pdf_parser.py    PDF bytes → sectioned profile text (pure, no network)
  analyzer.py      sections → Report via Claude (LLM client injected)
  models.py        Pydantic schemas (also the JSON contract for Claude)
  templates/
    upload.html    upload page
    report.html    report page (scores, critiques, rewrites, keywords)
docs/superpowers/specs/
  2026-07-14-linkedin-profile-agent-design.md   full design spec
tests/             unit + integration tests (LLM mocked)
```

---

## Development

Modules are intentionally small and independently testable:

- `pdf_parser` is pure — unit-tested against a sample PDF fixture.
- `analyzer` takes the Anthropic client as a parameter, so tests run against a
  **mocked** client (no network, no cost).
- `main` has one integration test for `POST /analyze` with the LLM mocked.

```bash
pytest
```

---

## Privacy

Your profile PDF is parsed locally and its text is sent to the Anthropic API
only for the duration of the analysis request. The app does not persist your
profile or the generated report.

---

## License

MIT (to be added).
