import sys
import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path to import sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.llm import get_llm
from etl.processor import ClaimProcessor
from indexing.vector_store import VectorStore

app = FastAPI(title="RAG Claims Assistant", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
vector_store = VectorStore(
    model_name=settings.EMBEDDING_MODEL,
    index_file=settings.INDEX_FILE,
    metadata_file=settings.METADATA_FILE
)
llm = None 
# specialized deferred loader for LLM to avoid startup delay if using local model
def get_app_llm():
    global llm
    if llm is None:
        llm = get_llm()
    return llm

# Models
class QueryRequest(BaseModel):
    query: str
    k: int = 5

class SourceDocument(BaseModel):
    doc_id: str
    claim_id: Optional[str]
    retrieval_score: float
    excerpt: str
    full_metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    metadata: dict

class IngestResponse(BaseModel):
    message: str
    num_records: int
    num_chunks: int

# Routes
@app.on_event("startup")
def startup_event():
    # Try to load existing index
    try:
        vector_store.load_index()
    except:
        print("No existing index found. Please run /ingest.")

@app.get("/health")
def health_check():
    return {"status": "ok", "index_size": vector_store.index.ntotal if vector_store.index else 0}

@app.post("/ingest", response_model=IngestResponse)
def ingest_data():
    """Reads the CSV, processes it, and rebuilds the index."""
    if not os.path.exists(settings.CLAIMS_CSV):
        raise HTTPException(status_code=404, detail="Claims data not found. Run data generator first.")
    
    start_time = time.time()
    
    processor = ClaimProcessor()
    records = processor.load_csv(settings.CLAIMS_CSV)
    documents = processor.process_records(records)
    
    vector_store.create_index(documents)
    vector_store.save_index()
    
    return {
        "message": "Ingestion complete",
        "num_records": len(records),
        "num_chunks": len(documents),
        "duration_seconds": time.time() - start_time
    }

# Helper for extracting filters
def extract_filters(query: str, current_llm) -> dict:
    """
    Uses the LLM to extract structured filters from the natural language query.
    Returns a dict like: {'start_date': '2023-01-01', 'status': 'Denied'}
    """
    # Simple prompt to extract JSON
    prompt = (
        "Extract metadata filters from the user query. \n"
        "Return ONLY a valid JSON object with keys: 'start_date' (YYYY-MM-DD), 'end_date' (YYYY-MM-DD), "
        "'status' (Approved, Denied, Pending), 'specialty', 'doctor_name', 'claim_id'. \n"
        "Date logic: 'last quarter' means previous 3 month block. 'last year' means 2023 (if current is 2024).\n"
        "If a filter is not present, omit the key.\n"
        "Example: 'Show me denied claims' -> {\"status\": \"Denied\"}\n"
        f"Query: {query}\n"
        "JSON:"
    )
    
    try:
        # Mock LLM doesn't support this well, so we hardcode a basic parser for 'mock' mode or fallback
        if settings.LLM_TYPE == "mock":
            filters = {}
            if "denied" in query.lower(): filters["status"] = "Denied"
            if "approved" in query.lower(): filters["status"] = "Approved"
            return filters
            
        # Real LLM extraction
        response_text = current_llm.generate_answer(prompt, []) # Pass empty context
        
        # Clean markdown code blocks if present
        import json
        import re
        
        cleaned = re.sub(r"```json|```", "", response_text).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end != -1:
             filters = json.loads(cleaned[start:end])
             return filters
    except Exception as e:
        print(f"Filter extraction failed: {e}")
        
    return {}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    if not vector_store.index or vector_store.index.ntotal == 0:
        raise HTTPException(status_code=400, detail="Index is empty. Please run /ingest first.")
        
    start_time = time.time()
    
    current_llm = get_app_llm()
    
    # 1. Extract Filters
    filters = extract_filters(request.query, current_llm)
    print(f"Extracted Filters: {filters}")
    
    # 2. Retrieval with Filters
    results = vector_store.search(request.query, k=request.k, filters=filters)
    
    # Format sources for LLM
    context = []
    sources_response = []
    
    for doc, score in results:
        context.append(doc)
        sources_response.append(SourceDocument(
            doc_id=doc['id'],
            claim_id=doc['metadata'].get('claim_id'),
            retrieval_score=score,
            excerpt=doc['text'],
            full_metadata=doc['metadata']
        ))
        
    # 3. Generation
    answer = current_llm.generate_answer(request.query, context)
    
    return {
        "answer": answer,
        "sources": sources_response,
        "metadata": {
            "processing_latency": time.time() - start_time,
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_type": settings.LLM_TYPE,
            "applied_filters": filters
        }
    }
