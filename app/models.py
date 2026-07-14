"""Pydantic schemas for parsed profiles and the analysis report.

The Report schema also serves as the JSON contract Claude must return.
"""

from pydantic import BaseModel, Field


class ProfileSections(BaseModel):
    """Raw profile text extracted from the PDF, one field per section."""

    headline: str = ""
    about: str = ""
    experience: str = ""
    education: str = ""
    skills: str = ""


class SectionResult(BaseModel):
    """Claude's assessment of a single profile section."""

    name: str
    score: int = Field(ge=0, le=100)
    critique: str
    rewrite: str


class Report(BaseModel):
    """The full analysis report returned to the browser."""

    overall_score: int = Field(ge=0, le=100)
    sections: list[SectionResult]
    keywords: list[str]
