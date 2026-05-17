import pytest
from rag.adaptive_learning import StrategyAdaptationEngine
from memory.schemas import EpisodicEvent

def test_strategy_adaptation():
    engine = StrategyAdaptationEngine()
    
    events = [
        EpisodicEvent(event_id="1", agent_id="A2", segment_id="s1", reasoning_trace="...", applied_theory="Speech Act", validation_score=0.9, was_successful=True),
        EpisodicEvent(event_id="2", agent_id="A2", segment_id="s2", reasoning_trace="...", applied_theory="Speech Act", validation_score=0.4, was_successful=False),
        EpisodicEvent(event_id="3", agent_id="A2", segment_id="s3", reasoning_trace="...", applied_theory="Gricean", validation_score=0.95, was_successful=True)
    ]
    
    engine.ingest_batch(events)
    ranking = engine.rank_theories()
    
    assert len(ranking) == 2
    assert ranking[0].theory_name == "Gricean"
    assert ranking[0].success_rate == 1.0
    assert ranking[1].theory_name == "Speech Act"
    assert ranking[1].success_rate == 0.5
