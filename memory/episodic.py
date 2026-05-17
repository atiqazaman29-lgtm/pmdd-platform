from typing import List, Dict, Any
from memory.schemas import EpisodicEvent
from memory.vector_store import VectorMemoryManager
import uuid
import json

class EpisodicMemoryEngine:
    """Stores and retrieves agent reasoning trajectories."""
    
    def __init__(self, vector_store: VectorMemoryManager):
        self.vector_store = vector_store
        
    async def log_event(self, event: EpisodicEvent):
        # In a real setup, we also write to Supabase Postgres here.
        text_representation = f"Agent {event.agent_id} analyzed {event.segment_id} using {event.applied_theory}. Success: {event.was_successful}. Trace: {event.reasoning_trace}"
        
        await self.vector_store.embed_and_store(
            texts=[text_representation],
            metadatas=[event.model_dump(mode="json")],
            ids=[event.event_id]
        )

    async def retrieve_lessons(self, query_context: str, theory_filter: str = None) -> List[EpisodicEvent]:
        filter_dict = {"was_successful": True}
        if theory_filter:
            filter_dict["applied_theory"] = theory_filter
            
        results = await self.vector_store.retrieve_similar(query_context, top_k=3, filter=filter_dict)
        events = []
        for r in results:
            # Reconstruct EpisodicEvent from metadata
            events.append(EpisodicEvent(**r["metadata"]))
        return events
