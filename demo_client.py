import requests
import time
import json
import os

BASE_URL = "http://localhost:8000"
OUTPUT_FILE = "outputs/demo_results.json"

QUERIES = [
    "Show me denied claims for diabetes patients last quarter.",
    "List claims denied for 'medical necessity' in 2024 with amount > 10,000.",
    "Which doctors have the highest denial rate for cardiology claims in 2023?",
    "Show me all pending claims for patient with ID P_12345."
]

def wait_for_backend():
    print("Waiting for backend to come online...")
    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/health")
            print("Backend is online!")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)
    return False

def run_demo():
    if not os.path.exists("outputs"):
        os.makedirs("outputs")

    if not wait_for_backend():
        print("Backend failed to start.")
        return

    print("Triggering Ingestion...")
    ingest_res = requests.post(f"{BASE_URL}/ingest")
    print("Ingestion Result:", ingest_res.json())

    results = []
    
    print("Running sample queries...")
    for q in QUERIES:
        print(f"\nQuery: {q}")
        start = time.time()
        res = requests.post(f"{BASE_URL}/query", json={"query": q, "k": 3})
        if res.status_code == 200:
            data = res.json()
            print(f"Answer: {data['answer']}")
            print(f"Sources: {[s['doc_id'] for s in data['sources']]}")
            results.append({
                "query": q,
                "response": data,
                "latency": time.time() - start
            })
        else:
            print(f"Error: {res.text}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDemo complete. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_demo()
