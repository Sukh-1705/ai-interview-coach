"""Pydantic schemas for structured LLM outputs and data validation."""

from typing import Literal
from pydantic import BaseModel, Field


class MissingSkillItem(BaseModel):
    """Represents a specific skill gap identified from the JD."""
    skill: str = Field(description="Name of the missing or required skill")
    importance: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Importance of this skill for the target role"
    )
    reason: str = Field(description="Why the job description requires this skill")


class GapAnalysisResult(BaseModel):
    """Result of the pre-interview gap analysis comparing Resume vs JD."""
    match_score: int = Field(
        ge=0, le=100,
        description="Overall match score from 0 to 100"
    )
    summary: str = Field(
        description="2-3 sentence overview of candidate fit against the JD"
    )
    matched_skills: list[str] = Field(
        default_factory=list,
        description="List of skills clearly present in both resume and JD"
    )
    missing_skills: list[MissingSkillItem] = Field(
        default_factory=list,
        description="List of required/preferred skills missing from the resume"
    )
    weak_areas: list[str] = Field(
        default_factory=list,
        description="Skills mentioned in resume but lacking depth, metrics, or evidence"
    )
    resume_red_flags: list[str] = Field(
        default_factory=list,
        description="General resume flaws like missing metrics, vague bullet points, formatting gaps"
    )


class AnswerScore(BaseModel):
    """Detailed score and critique for a candidate's answer to an interview question."""
    relevance: int = Field(
        ge=1, le=10,
        description="Score (1-10) for how directly the answer addresses the question & role"
    )
    depth: int = Field(
        ge=1, le=10,
        description="Score (1-10) for technical or experiential detail, specific examples"
    )
    structure: int = Field(
        ge=1, le=10,
        description="Score (1-10) for logical flow, organization, STAR technique"
    )
    clarity: int = Field(
        ge=1, le=10,
        description="Score (1-10) for concise, articulate, and confident communication"
    )
    strengths: str = Field(
        description="One-sentence highlight of what was done well"
    )
    weaknesses: str = Field(
        description="One-sentence highlight of what was lacking or could be improved"
    )
    improved_answer: str = Field(
        description="A significantly stronger sample answer (using STAR framework where appropriate)"
    )

    @property
    def average(self) -> float:
        """Calculate the arithmetic mean of the 4 dimension scores."""
        return round((self.relevance + self.depth + self.structure + self.clarity) / 4.0, 2)
