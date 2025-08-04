# Axura RAG System 🤖

Sistema de **Retrieval-Augmented Generation (RAG)** para Axura que permite al asistente personal responder preguntas sobre todos los datos empresariales.

## 🚀 Características

- **Chunking inteligente** de documentos empresariales
- **Embeddings vectoriales** con OpenAI text-embedding-3-large
- **Base de datos vectorial** ChromaDB
- **Búsqueda semántica** de información relevante
- **Respuestas contextuales** con GPT-4
- **Procesamiento automático** de nuevos archivos
- **Integración con MongoDB** existente de Axura

## 📁 Estructura del Proyecto

```
axura-rag-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── models/                # Pydantic models
│   ├── services/              # Business logic
│   │   ├── chunking.py        # Text chunking service
│   │   ├── embeddings.py      # Embedding service
│   │   ├── vector_store.py    # ChromaDB operations
│   │   ├── rag_service.py     # Main RAG logic
│   │   └── data_processor.py  # Data extraction from MongoDB
│   └── api/                   # API routes
│       ├── __init__.py
│       └── routes.py          # FastAPI routes
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables
└── README.md                 # This file
```

## 🛠️ Instalación

1. **Clonar y configurar:**
```bash
cd axura-rag-backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp env.example .env
# Editar .env con tus credenciales
```

3. **Ejecutar el servidor:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### POST `/api/v1/ask`
Pregunta al asistente RAG sobre los datos empresariales.

**Request:**
```json
{
  "question": "¿Cuántos productos tengo en stock bajo?",
  "user_id": "user_id_here",
  "company_id": "company_id_here"
}
```

**Response:**
```json
{
  "answer": "Según los datos de tu empresa, tienes 3 productos con stock bajo: Producto A (5/10), Producto B (2/8), Producto C (1/5).",
  "sources": [
    {
      "type": "inventory",
      "content": "Producto A - Stock actual: 5, Stock mínimo: 10",
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "total_sources": 5,
    "processing_time": 1.2
  }
}
```

### POST `/api/v1/index`
Indexa nuevos documentos o datos.

**Request:**
```json
{
  "data_type": "inventory",
  "company_id": "company_id_here",
  "force_reindex": false
}
```

## 🔧 Configuración

### Variables de Entorno

- `OPENAI_API_KEY`: Tu clave de API de OpenAI
- `MONGODB_URI`: URI de conexión a MongoDB
- `CHROMA_PERSIST_DIRECTORY`: Directorio para ChromaDB
- `OPENAI_MODEL`: Modelo de OpenAI para respuestas (default: gpt-4-1106-preview)
- `EMBEDDING_MODEL`: Modelo de embeddings (default: text-embedding-3-large)

## 🧪 Testing

```bash
pytest tests/
```

## 📊 Tipos de Datos Soportados

- **Facturas**: PDF, DOCX, XLSX
- **Inventario**: Productos, materias primas
- **Ventas**: Transacciones, reportes
- **Clientes**: Información de clientes
- **Configuración**: Ajustes empresariales

## 🔄 Integración con Axura

El sistema se conecta a la base de datos MongoDB existente de Axura para:

1. **Extraer datos** automáticamente
2. **Procesar y chunkear** el contenido
3. **Generar embeddings** vectoriales
4. **Indexar** en ChromaDB
5. **Responder preguntas** contextuales

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. 