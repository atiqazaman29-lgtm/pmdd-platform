from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ReportCitation(BaseModel):
    segment_id: str
    exact_quote: str
    agent_id: str
    theory_applied: str
    reliability_score: float

class ReportSection(BaseModel):
    title: str
    content: str
    citations: List[ReportCitation] = Field(default_factory=list)
    visualizations: List[str] = Field(default_factory=list)
    ambiguity_warnings: List[str] = Field(default_factory=list)

class FinalResearchReport(BaseModel):
    corpus_id: str
    title: str
    executive_summary: str
    sections: List[ReportSection]
    overall_reliability: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)
