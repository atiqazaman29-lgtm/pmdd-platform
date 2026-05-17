import pytest
from agents.agent1_preprocessor import CorpusPreprocessor

@pytest.mark.asyncio
async def test_agent1_ingestion():
    agent = CorpusPreprocessor()
    text = "This is the first sentence. And here is the second sentence! Wow, a third?"
    metadata = {"year": 2024, "genre": "test"}
    
    segments = await agent.ingest_file(text, metadata)
    assert len(segments) > 0
    assert segments[0].metadata["year"] == 2024
    
@pytest.mark.asyncio
async def test_agent1_empty_file():
    agent = CorpusPreprocessor()
    with pytest.raises(ValueError):
        await agent.ingest_file("   ", {})
