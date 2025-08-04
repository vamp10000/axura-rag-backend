"""
Example usage of Axura RAG System
"""
import asyncio
import json
from app.services.rag_service import RAGService


async def main():
    """Example usage of the RAG system"""
    print("🚀 Axura RAG System - Example Usage")
    print("=" * 50)
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Test system stats
    print("\n📊 System Statistics:")
    stats = await rag_service.get_system_stats()
    print(json.dumps(stats, indent=2, default=str))
    
    # Example company ID (replace with actual company ID)
    company_id = "687c9b11c2e913dd5a3de464"  # Replace with actual company ID
    
    # Index company data
    print(f"\n🚀 Indexing data for company {company_id}...")
    index_result = await rag_service.index_company_data(
        company_id=company_id,
        data_type="inventory",  # Start with inventory
        force_reindex=True
    )
    print(f"Indexing result: {index_result}")
    
    # Ask questions
    questions = [
        "¿Cuántos productos tengo en mi inventario?",
        "¿Qué productos tienen stock bajo?",
        "¿Cuál es el valor total de mi inventario?",
        "¿Cuántas materias primas tengo?",
        "¿Qué productos están activos?"
    ]
    
    print(f"\n🤖 Asking questions about company {company_id}:")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Pregunta: {question}")
        
        result = await rag_service.ask_question(
            question=question,
            user_id="example_user",
            company_id=company_id,
            max_sources=3,
            similarity_threshold=0.7
        )
        
        print(f"Respuesta: {result['answer']}")
        print(f"Fuentes encontradas: {len(result['sources'])}")
        
        if result['sources']:
            print("Fuentes:")
            for j, source in enumerate(result['sources'][:2], 1):
                print(f"  {j}. {source.type} (relevancia: {source.relevance_score:.2f})")
                print(f"     {source.content[:100]}...")
        
        print(f"Tiempo de procesamiento: {result['metadata'].get('processing_time', 0):.2f}s")
        print("-" * 30)


if __name__ == "__main__":
    asyncio.run(main()) 