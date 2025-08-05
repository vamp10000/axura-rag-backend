import os
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from app.config.settings import settings

class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.chroma_persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collections = {}

    async def _initialize_collections(self):
        """Initialize ChromaDB collections"""
        try:
            collection_names = [
                "products",
                "raw_materials", 
                "inventory_movements",
                "company_info"
            ]
            for name in collection_names:
                try:
                    collection = self.client.get_or_create_collection(
                        name=name,
                        metadata={"description": f"Collection for {name}"}
                    )
                    self.collections[name] = collection
                except Exception as e:
                    print(f"❌ Error creating collection {name}: {e}")
        except Exception as e:
            print(f"❌ Error initializing collections: {e}")

    async def add_documents(self, collection_name: str, documents: List[str], 
                           metadatas: List[Dict[str, Any]], ids: List[str]) -> bool:
        """Add documents to a collection"""
        try:
            if collection_name not in self.collections:
                await self._initialize_collections()
            if collection_name not in self.collections:
                print(f"❌ Collection {collection_name} not found")
                return False
            
            collection = self.collections[collection_name]
            
            # Process in batches to avoid memory issues
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
            
            return True
        except Exception as e:
            print(f"❌ Error adding documents to {collection_name}: {e}")
            return False

    async def search_similar(self, collection_name: str, query_embedding: List[float], 
                           n_results: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if collection_name not in self.collections:
                await self._initialize_collections()
            if collection_name not in self.collections:
                print(f"❌ Collection {collection_name} not found")
                return []
            
            collection = self.collections[collection_name]
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            similar_docs = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    similarity = 1 - distance
                    if similarity >= threshold:
                        similar_docs.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "distance": distance
                        })
            
            return similar_docs
        except Exception as e:
            print(f"❌ Error searching in {collection_name}: {e}")
            return []

    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            if collection_name not in self.collections:
                await self._initialize_collections()
            if collection_name not in self.collections:
                return {"error": f"Collection {collection_name} not found"}
            
            collection = self.collections[collection_name]
            count = collection.count()
            
            return {
                "name": collection_name,
                "document_count": count,
                "status": "active"
            }
        except Exception as e:
            print(f"❌ Error getting stats for {collection_name}: {e}")
            return {"error": str(e)}

    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            await self._initialize_collections()
            stats = {}
            total_documents = 0
            
            for name, collection in self.collections.items():
                try:
                    count = collection.count()
                    stats[name] = {
                        "document_count": count,
                        "status": "active"
                    }
                    total_documents += count
                except Exception as e:
                    stats[name] = {"error": str(e)}
            
            return {
                "collections": stats,
                "total_collections": len(self.collections),
                "total_documents": total_documents
            }
        except Exception as e:
            print(f"❌ Error getting all stats: {e}")
            return {"error": str(e)}

    async def test_connection(self) -> bool:
        """Test ChromaDB connection"""
        try:
            await self._initialize_collections()
            stats = await self.get_all_stats()
            return "error" not in stats
        except Exception as e:
            print(f"❌ ChromaDB connection test failed: {e}")
            return False

    async def clear_collection(self, collection_name: str) -> bool:
        """Clear a collection"""
        try:
            if collection_name not in self.collections:
                await self._initialize_collections()
            if collection_name not in self.collections:
                return False
            
            collection = self.collections[collection_name]
            collection.delete(where={})
            return True
        except Exception as e:
            print(f"❌ Error clearing collection {collection_name}: {e}")
            return False
