"""
modules/resume_data.py
Structured dataclass for extracted resume data in ResumeIQ v2.0.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ResumeData:
    candidate_name: str = "Name not confidently detected"
    target_role: str = ""
    email: str = "Not Found"
    phone: str = "Not Found"
    address: str = "Not Found"
    linkedin: str = "Not Found"
    github: str = "Not Found"
    portfolio: str = "Not Found"
    website: str = "Not Found"
    
    languages: List[str] = field(default_factory=list)
    education: List[Dict[str, str]] = field(default_factory=list)
    experience: List[Dict[str, str]] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[Dict[str, str]] = field(default_factory=list)
    publications: List[str] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)
    volunteer: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    
    raw_text: str = ""
    file_format: str = "pdf"
    file_path: str = ""
    is_linkedin_export: bool = False
    is_europass: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumeData':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
