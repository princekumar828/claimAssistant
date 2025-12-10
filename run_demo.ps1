Write-Host "Starting RAG Claims Assistant Demo..."

# 1. Generate Data
Write-Host "Generating Synthetic Data..."
python data_gen/generate_synthetic_claims.py

# 2. Start Infrastructure
Write-Host "Starting Docker Containers..."
docker-compose up -d --build

# 3. Run Client Demo
Write-Host "Running Demo Client..."
# Ensure requests is installed for the client script
pip install requests

python demo_client.py

Write-Host "Demo Complete. Access the UI at http://localhost:3000"
Write-Host "Press any key to exit..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
