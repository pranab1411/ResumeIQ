from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ResumeAnalysisResult:
    resume_id: int
    filename: str
    ats_score: float
    job_title: str
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extracted_contact: dict = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    score_category: str = "Average"
