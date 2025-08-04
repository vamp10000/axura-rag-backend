"""
Main FastAPI application for Axura RAG System
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Axura RAG System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "axura-rag"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "axura-rag"}
# Updated main.py
# Updated main.py with working endpoints
# Updated main.py
