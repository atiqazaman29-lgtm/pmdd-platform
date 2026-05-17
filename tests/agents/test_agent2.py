import pytest
import os
from agents.agent2_pragmatic import PragmaticAnalyzerAgent
from agents.schemas import CognitiveState, CorpusSegment

@pytest.mark.asyncio
async def test_agent2_analyze():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
        
    agent = PragmaticAnalyzerAgent()
    segment = CorpusSegment(
        segment_id="test-123",
        raw_text="It's a bit cold in here, isn't it? [Looking at the open window]",
        metadata={}
    )
    state = CognitiveState(session_id="session-1", segment=segment)
    
    output = await agent.execute(state)
    assert output is not None
    assert output.validation_status == "Passed"
    assert len(output.findings) > 0
    
    # Check if implicature was detected
    theory_text = str([f.linguistic_theory for f in output.findings]).lower()
    assert "act" in theory_text or "implicature" in theory_text or "request" in theory_text
