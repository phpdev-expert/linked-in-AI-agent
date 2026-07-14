import pytest

from app.analyzer import analyze
from app.models import Report
from tests.conftest import FakeClient


def test_analyze_returns_report(sample_sections, valid_report_json):
    client = FakeClient([valid_report_json])
    report = analyze(sample_sections, client=client, model="test-model")
    assert isinstance(report, Report)
    assert report.overall_score == 78
    assert report.sections[0].name == "Headline"
    assert "python" in report.keywords


def test_analyze_sends_sections_and_rubric_in_prompt(sample_sections, valid_report_json):
    client = FakeClient([valid_report_json])
    analyze(sample_sections, client=client, model="test-model")
    sent = client.messages.calls[0]
    prompt = sent["messages"][0]["content"]
    assert "Jane Developer" in prompt
    assert "reliable APIs" in prompt
    assert "millions of requests" in prompt
    assert "Headline" in prompt and "keyword" in prompt.lower()
    assert sent["model"] == "test-model"


def test_analyze_retries_once_on_malformed_json(sample_sections, valid_report_json):
    client = FakeClient(["not json at all", valid_report_json])
    report = analyze(sample_sections, client=client, model="test-model")
    assert report.overall_score == 78
    assert len(client.messages.calls) == 2


def test_analyze_raises_after_second_failure(sample_sections):
    client = FakeClient(["nope", "still nope"])
    with pytest.raises(ValueError):
        analyze(sample_sections, client=client, model="test-model")


def test_analyze_extracts_json_from_fenced_block(sample_sections, valid_report_json):
    fenced = f"Here is the report:\n```json\n{valid_report_json}\n```"
    client = FakeClient([fenced])
    report = analyze(sample_sections, client=client, model="test-model")
    assert report.overall_score == 78


def test_analyze_extracts_json_when_prose_contains_inline_fence(sample_sections, valid_report_json):
    fenced = f"Try using ```python``` in skills.\n\n```json\n{valid_report_json}\n```"
    client = FakeClient([fenced])
    report = analyze(sample_sections, client=client, model="test-model")
    assert report.overall_score == 78
