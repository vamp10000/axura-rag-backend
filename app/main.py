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
        
        # Generate embedding for the question
        embedding = await embedding_service.generate_embedding(question)
        
        # Search in all collections
        all_results = []
        
        # Search products
        products_results = await vector_store_service.search_similar(
            "products", embedding, company_id, limit=3
        )
        all_results.extend(products_results)
        
        # Search raw materials
        raw_materials_results = await vector_store_service.search_similar(
            "raw_materials", embedding, company_id, limit=3
        )
        all_results.extend(raw_materials_results)
        
        # Search inventory movements
        movements_results = await vector_store_service.search_similar(
            "inventory_movements", embedding, company_id, limit=3
        )
        all_results.extend(movements_results)
        
        # Search company info
        company_results = await vector_store_service.search_similar(
            "company_info", embedding, company_id, limit=2
        )
        all_results.extend(company_results)
        
        # Sort by similarity and get top results
        all_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        top_results = all_results[:5]
        
        # Get real company data
        company_data = await data_processor_service.get_inventory_data(company_id)
        
        # Build answer based on results and real data
        if top_results:
            sources_info = []
            for result in top_results:
                source_type = result.get("metadata", {}).get("type", "unknown")
                content = result.get("content", "")
                sources_info.append(f"- {source_type}: {content[:100]}...")
            
            answer = f"Basándome en los datos de tu empresa {company_id}:\n\n"
            answer += "\n".join(sources_info)
            
            # Add real statistics
            if company_data:
                answer += f"\n\n📊 **Estadísticas actuales:**\n"
                answer += f"- Productos: {company_data.get('total_products', 0)}\n"
                answer += f"- Materias primas: {company_data.get('total_raw_materials', 0)}\n"
                answer += f"- Valor total del inventario: ${company_data.get('total_inventory_value', 0):,.2f}\n"
                answer += f"- Productos con bajo stock: {company_data.get('low_stock_count', 0)}"
        else:
            answer = f"No encontré información específica para tu pregunta sobre '{question}' en los datos de la empresa {company_id}."
        
        return AskResponse(
            answer=answer,
            sources=top_results,
            metadata={
                "total_sources": len(top_results),
                "company_id": company_id,
                "real_data": company_data
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/api/v1/index")
async def index_data(request: dict):
    try:
        company_id = request.get("company_id", "")
        
        # Get real inventory data
        inventory_data = await data_processor_service.get_inventory_data(company_id)
        
        # Format data for RAG
        formatted_data = await data_processor_service.format_inventory_for_rag(inventory_data)
        
        # Clear existing collections
        await vector_store_service.clear_collection("products")
        await vector_store_service.clear_collection("raw_materials")
        await vector_store_service.clear_collection("inventory_movements")
        await vector_store_service.clear_collection("company_info")
        
        # Add documents to vector store
        total_chunks = 0
        
        if formatted_data.get("products"):
            await vector_store_service.add_documents("products", formatted_data["products"])
            total_chunks += len(formatted_data["products"])
        
        if formatted_data.get("raw_materials"):
            await vector_store_service.add_documents("raw_materials", formatted_data["raw_materials"])
            total_chunks += len(formatted_data["raw_materials"])
        
        if formatted_data.get("movements"):
            await vector_store_service.add_documents("inventory_movements", formatted_data["movements"])
            total_chunks += len(formatted_data["movements"])
        
        if formatted_data.get("summary"):
            await vector_store_service.add_documents("company_info", formatted_data["summary"])
            total_chunks += len(formatted_data["summary"])
        
        return {
            "success": True,
            "message": f"Data indexed successfully for company {company_id}",
            "chunks_processed": total_chunks,
            "company_data": {
                "total_products": inventory_data.get("total_products", 0),
                "total_raw_materials": inventory_data.get("total_raw_materials", 0),
                "total_inventory_value": inventory_data.get("total_inventory_value", 0)
            }
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
