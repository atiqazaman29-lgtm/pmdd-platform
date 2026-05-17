from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class EpisodicEvent(BaseModel):
    event_id: str
    agent_id: str
    segment_id: str
    reasoning_trace: str
    applied_theory: str
    validation_score: float = Field(..., ge=0.0, le=1.0)
    was_successful: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RetrievalContext(BaseModel):
    query_text: str
    similar_episodes: List[EpisodicEvent]
    semantic_drift_examples: List[Dict[str, Any]]
    confidence_decay: float = 1.0

class StrategyMetrics(BaseModel):
    theory_name: str
    success_rate: float
    usage_count: int
    average_confidence: float
