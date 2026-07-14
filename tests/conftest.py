import json

import pytest

from app.models import ProfileSections


@pytest.fixture
def sample_sections() -> ProfileSections:
    return ProfileSections(
        headline="Jane Developer\nSenior Backend Engineer at Acme",
        about="Experienced engineer who builds reliable APIs.",
        experience="Senior Backend Engineer at Acme\nBuilt services handling millions of requests.",
        education="BSc Computer Science, State University",
        skills="Python, FastAPI, PostgreSQL",
    )


@pytest.fixture
def valid_report_json() -> str:
    return json.dumps(
        {
            "overall_score": 78,
            "sections": [
                {"name": "Headline", "score": 65, "critique": "Generic.", "rewrite": "Better headline."},
                {"name": "About", "score": 80, "critique": "Solid.", "rewrite": "Even better about."},
            ],
            "keywords": ["python", "fastapi", "postgresql"],
        }
    )


class FakeMessages:
    """Mimics client.messages; returns queued responses in order."""

    def __init__(self, texts: list[str]):
        self._texts = list(texts)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = self._texts.pop(0)
        return type(
            "Resp", (), {"content": [type("Block", (), {"text": text})()]}
        )()


class FakeClient:
    """Stand-in for anthropic.Anthropic with queued message responses."""

    def __init__(self, texts: list[str]):
        self.messages = FakeMessages(texts)
