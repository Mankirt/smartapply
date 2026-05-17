from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Resume ──

class ResumeSection(BaseModel):
    section_type: str    # "experience", "skills", "education"
    title: str           # original heading text
    content: str         # body text of the section
    order: int           # position in the original resume


class ResumeResponse(BaseModel):
    id: int
    filename: str
    sections: list[ResumeSection]
    created_at: datetime


# ── Analysis ──

class AnalyzeRequest(BaseModel):
    resume_id: int
    jd_text: str = Field(..., min_length=50)
    company_name: str = Field(..., min_length=1)
    role: str | None = None

class BulletSuggestion(BaseModel):
    original: str
    improved: str
    reason: str    


class SectionAnalysis(BaseModel):
    section_type: str
    section_title: str
    similarity_score: float   
    suggestions: list[BulletSuggestion]
    status: str = "pending"   # pending | accepted | edited | ignored


class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    fit_score: int
    matching_skills: list[str]
    missing_keywords: list[str]
    summary: str
    sections: list[SectionAnalysis]
    company_name: str | None = None
    role: str | None = None
    created_at: datetime


# ── Review (Accept/Edit/Ignore) ──

class SectionReviewUpdate(BaseModel):
    section_type: str
    status: str                        # "accepted" | "edited" | "ignored"
    edited_content: Optional[str] = None  # only set if status == "edited"


# ── History ──

class AnalysisSummary(BaseModel):
    id: int
    resume_id: int
    fit_score: int
    summary: str
    company_name: str | None = None
    role: str | None = None
    resume_filename: str | None = None   
    created_at: datetime