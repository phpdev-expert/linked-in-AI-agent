"""Send parsed profile sections to Claude and return a validated Report.

The Anthropic client is injected so tests can pass a fake. No client is
constructed here.
"""

import json

from pydantic import ValidationError

from app.models import ProfileSections, Report

MAX_TOKENS = 4096

_RUBRIC = """You are a LinkedIn profile coach. Score each section 0-100 against
these best practices:
- Headline: more than a job title; states value/specialty; keyword-rich.
- About: strong hook in the first lines; first person; quantified impact; clear call to action.
- Experience: achievement-oriented bullets with metrics, not a list of duties.
- Skills: covers relevant industry terms so recruiter searches surface the person.
- Completeness: every section present with meaningful depth.

For each section give a score, a specific critique, and a ready-to-paste rewrite.
Then give an overall score (0-100) and a list of suggested keywords/skills to
improve searchability."""

_OUTPUT_CONTRACT = """Return ONLY a JSON object, no prose, matching exactly:
{
  "overall_score": <int 0-100>,
  "sections": [
    {"name": "Headline", "score": <int 0-100>, "critique": "<text>", "rewrite": "<text>"},
    {"name": "About", "score": <int>, "critique": "<text>", "rewrite": "<text>"},
    {"name": "Experience", "score": <int>, "critique": "<text>", "rewrite": "<text>"},
    {"name": "Education", "score": <int>, "critique": "<text>", "rewrite": "<text>"},
    {"name": "Skills", "score": <int>, "critique": "<text>", "rewrite": "<text>"}
  ],
  "keywords": ["<keyword>", ...]
}"""


def _build_prompt(sections: ProfileSections) -> str:
    return (
        f"{_RUBRIC}\n\n"
        "Here is the profile, section by section:\n\n"
        f"## Headline\n{sections.headline or '(missing)'}\n\n"
        f"## About\n{sections.about or '(missing)'}\n\n"
        f"## Experience\n{sections.experience or '(missing)'}\n\n"
        f"## Education\n{sections.education or '(missing)'}\n\n"
        f"## Skills\n{sections.skills or '(missing)'}\n\n"
        f"{_OUTPUT_CONTRACT}"
    )


def _extract_json(text: str) -> str:
    """Pull a JSON object out of the response, tolerating ```json fences."""
    if "```" in text:
        fenced = text.split("```", 2)[1]
        if fenced.startswith("json"):
            fenced = fenced[len("json"):]
        text = fenced
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return text[start : end + 1]


def _call(client, model: str, prompt: str) -> str:
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def analyze(sections: ProfileSections, client, model: str) -> Report:
    """Analyze the profile with Claude and return a validated Report.

    Retries once if the model returns malformed JSON. Raises ValueError if the
    second attempt also fails to parse/validate.
    """
    prompt = _build_prompt(sections)
    last_error: Exception | None = None
    for _ in range(2):
        raw = _call(client, model, prompt)
        try:
            return Report.model_validate_json(_extract_json(raw))
        except (ValueError, ValidationError, json.JSONDecodeError) as exc:
            last_error = exc
    raise ValueError(f"Claude did not return a valid report: {last_error}")
