from typing import TypedDict, List, Dict, Any

class PMDDState(TypedDict):
    corpus_id: str
    segment_id: str
    raw_text: str
    agent_outputs: Dict[str, Any]
    validation_status: str
    retry_count: int
    final_report_uri: str
