from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HallucinationScore(BaseModel):
    is_hallucinated: bool
    fabricated_quotes: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)

class ContradictionReport(BaseModel):
    has_contradiction: bool
    conflicting_findings: List[Dict[str, Any]] = Field(default_factory=list)
    resolution_suggestion: str = ""

class ReliabilityMetrics(BaseModel):
    evidence_strength_score: float = Field(..., ge=0.0, le=1.0)
    theoretical_defensibility_score: float = Field(..., ge=0.0, le=1.0)
    statistical_support_score: float = Field(..., ge=0.0, le=1.0)
    hallucination_penalty: float = Field(default=0.0)
    overall_reliability_score: float = Field(..., ge=0.0, le=1.0)
    is_academically_defensible: bool

class ReviewerAnnotation(BaseModel):
    reviewer_id: str
    finding_id: str
    approved: bool
    comments: str
    override_interpretation: Optional[str] = None
