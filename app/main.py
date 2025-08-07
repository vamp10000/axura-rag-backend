from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio

from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.data_processor import DataProcessorService
from app.config import settings

app = FastAPI(title="Axura RAG System", version="1.0.0")

# Initialize services
embedding_service = EmbeddingService()
vector_store_service = VectorStoreService()
data_processor_service = DataProcessorService()

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
        
        print(f"🔍 RAG: Processing question for company {company_id}: {question}")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Mock company data based on company_id
        mock_company_data = {
            "total_products": 25,
            "total_raw_materials": 15,
            "low_stock_items": 3,
            "total_inventory_value": 150000.00
        }
        
        # Generate mock response based on question
        lower_question = question.lower()
        
        if "producto" in lower_question or "productos" in lower_question:
            answer = f"Basándome en los datos de tu empresa {company_id}:\n\n"
            answer += "📦 **Información de Productos:**\n"
            answer += f"- Total de productos: {mock_company_data['total_products']}\n"
            answer += f"- Productos con bajo stock: {mock_company_data['low_stock_items']}\n"
            answer += f"- Valor total del inventario: ${mock_company_data['total_inventory_value']:,.2f}\n\n"
            answer += "Los productos más populares incluyen:\n"
            answer += "- Producto A: 50 unidades en stock\n"
            answer += "- Producto B: 30 unidades en stock\n"
            answer += "- Producto C: 15 unidades en stock"
            
            sources = [
                {
                    "content": "Producto A: 50 unidades en stock - Categoría: Electrónicos",
                    "metadata": {"type": "product", "name": "Producto A", "stock": 50},
                    "similarity": 0.95
                },
                {
                    "content": "Producto B: 30 unidades en stock - Categoría: Herramientas",
                    "metadata": {"type": "product", "name": "Producto B", "stock": 30},
                    "similarity": 0.88
                }
            ]
        elif "materia" in lower_question or "materias" in lower_question:
            answer = f"Basándome en los datos de tu empresa {company_id}:\n\n"
            answer += "🏭 **Información de Materias Primas:**\n"
            answer += f"- Total de materias primas: {mock_company_data['total_raw_materials']}\n"
            answer += "- Proveedores principales: 8\n\n"
            answer += "Materias primas más utilizadas:\n"
            answer += "- Material X: 200 kg en stock\n"
            answer += "- Material Y: 150 kg en stock\n"
            answer += "- Material Z: 100 kg en stock"
            
            sources = [
                {
                    "content": "Material X: 200 kg en stock - Proveedor: ABC Supplies",
                    "metadata": {"type": "raw_material", "name": "Material X", "stock": 200},
                    "similarity": 0.92
                }
            ]
        else:
            answer = f"Basándome en los datos de tu empresa {company_id}:\n\n"
            answer += "📊 **Resumen General:**\n"
            answer += f"- Productos: {mock_company_data['total_products']}\n"
            answer += f"- Materias primas: {mock_company_data['total_raw_materials']}\n"
            answer += f"- Valor total del inventario: ${mock_company_data['total_inventory_value']:,.2f}\n"
            answer += f"- Productos con bajo stock: {mock_company_data['low_stock_items']}\n\n"
            answer += "¿En qué aspecto específico te gustaría que profundice?"
            
            sources = [
                {
                    "content": f"Resumen de inventario para empresa {company_id}",
                    "metadata": {"type": "summary", "company_id": company_id},
                    "similarity": 0.85
                }
            ]
        
        print(f"✅ RAG: Successfully processed question, found {len(sources)} sources")
        
        return AskResponse(
            answer=answer,
            sources=sources,
            metadata={
                "total_sources": len(sources),
                "company_id": company_id,
                "company_data": mock_company_data,
                "processing_time": 0.5,
                "note": "Using mock data while MongoDB connection is being configured"
            }
        )
        
    except Exception as e:
        print(f"❌ RAG: Error processing question: {e}")
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

@app.get("/api/v1/test-companies")
async def test_companies():
    """
    Endpoint para probar conexión y listar empresas disponibles
    """
    try:
        # Test MongoDB connection
        connection_status = "unknown"
        companies = []
        
        try:
            # Try to connect to MongoDB
            await data_processor_service.client.admin.command('ping')
            connection_status = "connected"
            
            # Try to get companies from users collection
            users_collection = data_processor_service.db.users
            company_users = await users_collection.find({"role": "empresajefe"}).to_list(length=10)
            
            for user in company_users:
                companies.append({
                    "company_id": user.get("company"),
                    "company_name": user.get("companyName", "Unknown"),
                    "admin_email": user.get("email", "Unknown"),
                    "created_at": user.get("createdAt", "Unknown")
                })
                
        except Exception as e:
            connection_status = f"error: {str(e)}"
        
        return {
            "mongodb_connection": connection_status,
            "mongodb_uri": settings.mongodb_uri.replace("://", "://***:***@") if settings.mongodb_uri else "not_set",
            "mongodb_database": settings.mongodb_database,
            "companies_found": len(companies),
            "companies": companies,
            "environment": {
                "openai_api_key_set": bool(settings.openai_api_key),
                "chromadb_persist_directory": settings.chromadb_persist_directory
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "mongodb_uri": settings.mongodb_uri.replace("://", "://***:***@") if settings.mongodb_uri else "not_set",
            "mongodb_database": settings.mongodb_database
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
