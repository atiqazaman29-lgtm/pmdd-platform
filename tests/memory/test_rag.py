import pytest
from unittest.mock import AsyncMock, MagicMock
from rag.retriever import RAGOrchestrator
from memory.vector_store import VectorMemoryManager
from memory.episodic import EpisodicMemoryEngine
from memory.schemas import RetrievalContext

@pytest.mark.asyncio
async def test_rag_retrieval():
    # Mock Vector Store
    mock_vs = MagicMock(spec=VectorMemoryManager)
    mock_vs.retrieve_similar = AsyncMock(return_value=[{"id": "doc1", "score": 0.9, "metadata": {}}])
    
    # Mock Episodic Engine
    mock_ep = MagicMock(spec=EpisodicMemoryEngine)
    mock_ep.retrieve_lessons = AsyncMock(return_value=[])
    
    rag = RAGOrchestrator(mock_vs, mock_ep)
    context = await rag.get_context("This is a test segment.")
    
    assert isinstance(context, RetrievalContext)
    assert len(context.semantic_drift_examples) == 1
    mock_ep.retrieve_lessons.assert_called_once()
