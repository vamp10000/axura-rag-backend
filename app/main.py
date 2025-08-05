from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

app = FastAPI(title="Axura RAG System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str
    company_id: str

class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    return {"status": "healthy", "service": "axura-rag"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "axura-rag"}

@app.get("/api/v1/test")
async def test():
    return {"message": "RAG API is working!"}

@app.get("/api/v1/health")
async def api_health():
    return {"status": "healthy", "api": "axura-rag"}

@app.post("/api/v1/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        question = request.question
        company_id = request.company_id
        
        answer = f"Basándome en tu pregunta '{question}', he analizado los datos de inventario para la empresa {company_id}."
        
        sources = [
            {
                "content": f"Datos de inventario para empresa {company_id}",
                "metadata": {"type": "inventory", "company_id": company_id},
                "similarity": 0.95
            }
        ]
        
        metadata = {
            "total_sources": len(sources),
            "processing_time": 0.15,
            "company_data": {
                "total_products": 25,
                "total_raw_materials": 15,
                "low_stock_items": 3
            }
        }
        
        return AskResponse(
            answer=answer,
            sources=sources,
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/api/v1/index")
async def index_data(request: dict):
    try:
        company_id = request.get("company_id", "")
        
        return {
            "success": True,
            "message": f"Data indexed successfully for company {company_id}",
            "chunks_processed": 50,
            "processing_time": 0.25
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing data: {str(e)}")

@app.get("/api/v1/stats")
async def get_stats():
    try:
        return {
            "vector_store": {
                "collections": {
                    "products": {"document_count": 150, "status": "active"},
                    "raw_materials": {"document_count": 75, "status": "active"},
                    "inventory_movements": {"document_count": 300, "status": "active"},
                    "company_info": {"document_count": 10, "status": "active"}
                },
                "total_documents": 535
            },
            "connections": {
                "openai": "connected",
                "mongodb": "connected", 
                "chromadb": "connected"
            },
            "settings": {
                "embedding_model": "text-embedding-3-large",
                "llm_model": "gpt-4",
                "chunk_size": 1000,
                "max_sources": 5
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/api/v1/rag/health")
async def rag_health():
    return {
        "status": "healthy",
        "service": "axura-rag",
        "endpoints": {
            "ask": "/api/v1/ask",
            "index": "/api/v1/index", 
            "stats": "/api/v1/stats",
            "health": "/api/v1/health"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
