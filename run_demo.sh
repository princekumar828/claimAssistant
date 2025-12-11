#!/bin/bash
set -e

echo "Starting RAG Claims Assistant Demo..."

# 1. Generate Data (if not already done, but running it again is safe)
echo "Generating Synthetic Data..."
python3 data_gen/generate_synthetic_claims.py

# 2. Start Infrastructure
echo "Starting Docker Containers..."
# Docker Compose will use the default 'mock' if LLM_TYPE is not set in shell
docker-compose up -d --build

echo "---------------------------------------------------"
echo "Stack started!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo ""
echo "To run the demo query script, run:"
echo "python3 demo_client.py"
echo "(Requires 'pip install requests')"
echo "---------------------------------------------------"
