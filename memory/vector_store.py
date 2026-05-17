import os
import logging
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger("pmdd.memory.vector")

class VectorMemoryManager:
    """Handles Pinecone vector database and OpenAI embeddings."""
    
    def __init__(self, index_name: str = "pmdd-memory"):
        self.index_name = index_name
        self.pc = None
        self.index = None
        self.embeddings = None
        
        # Initialize if keys are present
        if os.getenv("PINECONE_API_KEY") and os.getenv("OPENAI_API_KEY"):
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            self._ensure_index()
            
    def _ensure_index(self):
        if self.index_name not in [idx.name for idx in self.pc.list_indexes()]:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=3072,  # text-embedding-3-large dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        self.index = self.pc.Index(self.index_name)

    async def embed_and_store(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        if not self.index:
            logger.warning("Vector index not initialized.")
            return
            
        vectors = await self.embeddings.aembed_documents(texts)
        records = zip(ids, vectors, metadatas)
        
        # Chunking upserts
        batch_size = 100
        records_list = list(records)
        for i in range(0, len(records_list), batch_size):
            self.index.upsert(vectors=records_list[i:i+batch_size])

    async def retrieve_similar(self, query: str, top_k: int = 5, filter: Dict = None) -> List[Dict[str, Any]]:
        if not self.index:
            return []
            
        query_vec = await self.embeddings.aembed_query(query)
        results = self.index.query(
            vector=query_vec,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        return [{"id": match.id, "score": match.score, "metadata": match.metadata} for match in results.matches]
