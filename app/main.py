from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json

app = FastAPI(title="Axura RAG System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "healthy", "service": "axura-rag"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "axura-rag"}

@app.get("/api/v1/test")
async def test():
    return {"message": "RAG API is working!"}
