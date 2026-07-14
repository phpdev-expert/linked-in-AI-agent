from app.models import ProfileSections, SectionResult, Report


def test_profile_sections_defaults_to_empty_strings():
    sections = ProfileSections()
    assert sections.headline == ""
    assert sections.about == ""
    assert sections.experience == ""
    assert sections.education == ""
    assert sections.skills == ""


def test_report_round_trips_through_json():
    report = Report(
        overall_score=82,
        sections=[
            SectionResult(name="Headline", score=70, critique="Too generic.", rewrite="Better headline."),
        ],
        keywords=["python", "fastapi"],
    )
    dumped = report.model_dump_json()
    loaded = Report.model_validate_json(dumped)
    assert loaded.overall_score == 82
    assert loaded.sections[0].name == "Headline"
    assert loaded.keywords == ["python", "fastapi"]


def test_report_rejects_out_of_range_score():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Report(overall_score=150, sections=[], keywords=[])
