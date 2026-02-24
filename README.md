# RAG-Powered Claims Query Assistant

A professional, Dockerized RAG (Retrieval-Augmented Generation) system for querying insurance claims data using Natural Language. 
It combines **Vector Search** (semantic understanding) with **Metadata Filtering** (structured queries) to answer complex questions like *"Show me denied claims for diabetes patients last quarter"*. need improvements

## 🚀 Features

*   **Hybrid Search**: Combines semantic vector search (FAISS) with LLM-extracted metadata filters (Date, Status, Claim ID).
*   **Intelligent Query Parsing**: Uses LLMs to understand relative dates ("last quarter", "last year") and specific constraints.
*   **Data Generation**: Built-in tool to generate thousands of synthetic realistic insurance claims.
*   **Dockerized Architecture**: Fully isolated Frontend (React) and Backend (FastAPI) containers.
*   **Multi-LLM Support**: Easy switching between OpenAI, Google Gemini, and Local Models (GPT4All/Mock).
*   **Modern UI**: Responsive React interface with real-text streaming and source citations.

## 🛠️ Prerequisites

*   **Docker Desktop** (running)
*   **Git**
*   **API Key** (OpenAI or Google Gemini) - *Optional if using Local/Mock mode.*

## 🏁 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/princekumar828/claimAssistant.git
cd claimAssistant
```

### 2. Configure Environment
Create a `.env` file from the template:
```bash
cp .env.template .env
```
Open `.env` and add your API key:
```ini
LLM_TYPE=openai
OPENAI_API_KEY=sk-proj-...
# Or use LLM_TYPE=gemini / mock
```

### 3. Run the Application
**Mac / Linux:**
```bash
./run_demo.sh
```

**Windows:**
```powershell
docker-compose up -d --build
```
*Note: The system will automatically generate synthetic data if `sample_data/claims.csv` is missing.*

### 4. Access the UI
Open your browser to **[http://localhost:3000](http://localhost:3000)**.

---

## 💡 Usage Guide

### Ingesting Data
The system automatically ingests data on startup. To ingest new data:
1.  Place your CSV file at `sample_data/claims.csv` (Must match the [required schema](#csv-schema)).
2.  Click **"Re-Ingest Data"** in the UI, or run:
    ```bash
    curl -X POST http://localhost:8000/ingest
    ```

### Example Queries
Try asking these natural language questions:
*   *"Show me denied claims"*
*   *"Which claims were denied due to medical necessity?"*
*   *"Show me claims from last quarter"* (Temporal filtering)
*   *"Details for claim clm-0e74a86e"* (ID lookup)
*   *"List all cardiology claims above $1000"*

## 📊 CSV Schema
If you use your own data, ensure your CSV has these headers:
`claim_id`, `patient_id`, `doctor_name`, `specialty`, `diagnosis`, `procedure_code`, `claim_date` (YYYY-MM-DD), `amount`, `status`, `denial_reason`, `notes`.

## 🏗️ Architecture
*   **Frontend**: React, Vite, Tailwind CSS, Nginx.
*   **Backend**: FastAPI, Python 3.10.
*   **RAG Engine**: SentenceTransformers (`all-MiniLM-L6-v2`), FAISS (Vector DB).
*   **LLM Handling**: OpenAI API / Google Gemini API / GPT4All (Local).

## 🔧 Troubleshooting
*   **"Index empty"**: Click "Re-Ingest Data" in the UI.
*   **"Something went wrong"**: Check the browser console. If using OpenAI, ensure your API Key is valid and has credit.
*   **Docker errors**: Ensure Docker Desktop is running. Run `docker-compose down` and try again.

