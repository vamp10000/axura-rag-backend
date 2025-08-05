import os
import asyncio
from typing import Optional, List
import openai
from app.config.settings import settings

class EmbeddingService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        try:
            if not text.strip():
                return None
            response = await self.client.embeddings.create(
                model=self.model,
                input=text.strip()
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        try:
            if not texts:
                return []
            valid_texts = [text.strip() for text in texts if text.strip()]
            if not valid_texts:
                return []
            response = await self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            embeddings = []
            for data in response.data:
                embeddings.append(data.embedding)
            return embeddings
        except Exception as e:
            print(f"❌ Error generating batch embeddings: {e}")
            return []

    async def test_connection(self) -> bool:
        """Test OpenAI connection"""
        try:
            test_embedding = await self.generate_embedding("test")
            return test_embedding is not None
        except Exception as e:
            print(f"❌ OpenAI connection test failed: {e}")
            return False

    async def get_embedding_dimensions(self) -> Optional[int]:
        """Get embedding dimensions"""
        try:
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding) if test_embedding else None
        except Exception as e:
            print(f"❌ Error getting embedding dimensions: {e}")
            return None
