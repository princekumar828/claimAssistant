# RAG-Powered Claims Query Assistant

A complete local RAG system for querying insurance claims data using Natural Language.

## Features
- **Data Generation**: Synthetic claims generator.
- **RAG Pipeline**: Text normalization, embedding (SentenceTransformers), indexing (FAISS).
- **LLM Integration**: Supports Local (GPT4All) and Cloud (OpenAI).
- **UI**: Modern React Chat Interface with source citations.
- **Infrastructure**: Dockerized.

## Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Node.js (optional, for local frontend dev)

## Quick Start (Demo)
1. **Clone the repository**
2. **Run the Demo Script** (Windows PowerShell):
   ```powershell
   .\run_demo.ps1
   ```
   This will:
   - Generate 2000 mock claims.
   - build and start containers.
   - Run sample queries.
   - Save results to `outputs/demo_results.json`.

3. **Open UI**: Go to [http://localhost:3000](http://localhost:3000)

## Configuration
Edit `backend/config.py` or simple set env vars in `docker-compose.yml`:
- `LLM_TYPE`: `mock` (default), `gpt4all` (local), `openai`.
- `OPENAI_API_KEY`: Required if usage `openai`.

## Architecture
- **Frontend**: React + Vite (Port 3000)
- **Backend**: FastAPI (Port 8000)
- **Vector DB**: FAISS (Local file persistence)
- **ETL**: Custom Python scripts.

## Tradeoffs
- **Vector DB**: Used FAISS IndexFlatL2 for simplicity. For production, use Milvus or Weaviate.
- **LLM**: Defaulted to Mock/GPT4All for offline capability. 
- **Chunking**: Simple splitting. Production should use semantic chunking.
