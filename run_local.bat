@echo off
echo ==========================================
echo RAG Claims Assistant - Local Run Mode
echo ==========================================
echo.

echo [1/5] Installing Python Dependencies...
pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/5] Generating Synthetic Data...
python data_gen/generate_synthetic_claims.py

echo.
echo [3/5] Setting Environment Variables...
set PYTHONPATH=%CD%
set LLM_TYPE=gemini
set GEMINI_API_KEY=your-key-here
set EMBEDDING_MODEL=all-MiniLM-L6-v2

echo.
echo [4/5] Ingesting Data (Building Index)...
python -c "from backend.main import ingest_data; from backend.config import settings; print('Ingesting...'); ingest_data()"

echo.
echo [5/5] Starting Backend Server...
echo The Backend will run at http://localhost:8000
echo You can use the Demo Client in a new terminal: python demo_client.py
echo.
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
