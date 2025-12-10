import csv
import random
import uuid
from datetime import datetime, timedelta
import os

# Configuration
NUM_CLAIMS = 2000
OUTPUT_DIR = "sample_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "claims.csv")

# Constants / Mock Data data
SPECIALTIES = ["Cardiology", "Orthopedics", "Pediatrics", "Dermatology", "Oncology", "General Practice", "Neurology"]
DIAGNOSES = {
    "Cardiology": ["Hypertension", "Atrial Fibrillation", "Coronary Artery Disease", "Heart Failure"],
    "Orthopedics": ["Fracture", "Arthritis", "Tendonitis", "Sprain"],
    "Pediatrics": ["Otitis Media", "Viral Infection", "Asthma", "Chickenpox"],
    "Dermatology": ["Acne", "Eczema", "Psoriasis", "Dermatitis"],
    "Oncology": ["Lung Cancer", "Breast Cancer", "Leukemia", "Lymphoma"],
    "General Practice": ["Flu", "Common Cold", "Back Pain", "Headache"],
    "Neurology": ["Migraine", "Epilepsy", "Stroke", "Neuropathy"]
}

STATUSES = ["Approved", "Denied", "Pending"]
DENIAL_REASONS = [
    "Medical Necessity", "Prior Authorization Missing", "Duplicate Claim", 
    "Out of Network", "Coding Error", "Policy Terminated", "Experimental Treatment"
]

DOCTOR_NAMES = [
    "Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", "Dr. Jones", 
    "Dr. Garcia", "Dr. Miller", "Dr. Davis", "Dr. Rodriguez", "Dr. Martinez",
    "Dr. Hernandez", "Dr. Lopez", "Dr. Gonzalez", "Dr. Wilson", "Dr. Anderson"
]

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def generate_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_claims():
    ensure_dir(OUTPUT_DIR)
    
    headers = [
        "claim_id", "patient_id", "doctor_id", "doctor_name", "specialty", 
        "diagnosis", "procedure_code", "claim_date", "amount", 
        "status", "denial_reason", "notes"
    ]
    
    rows = []
    
    print(f"Generating {NUM_CLAIMS} synthetic claims...")
    
    for _ in range(NUM_CLAIMS):
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        patient_id = f"P-{random.randint(10000, 99999)}"
        
        doctor_name = random.choice(DOCTOR_NAMES)
        doctor_id = f"DR-{abs(hash(doctor_name)) % 10000}"
        
        specialty = random.choice(SPECIALTIES)
        diagnosis = random.choice(DIAGNOSES[specialty])
        
        # Weighted status
        status_roll = random.random()
        if status_roll < 0.6:
            status = "Approved"
            denial_reason = ""
        elif status_roll < 0.85:
            status = "Denied"
            denial_reason = random.choice(DENIAL_REASONS)
            # Correlate reason slightly
            if diagnosis in ["Acne", "Flu"] and random.random() < 0.3:
                denial_reason = "Medical Necessity"
        else:
            status = "Pending"
            denial_reason = ""
            
        claim_date = generate_date().strftime("%Y-%m-%d")
        
        # Amount logic
        base_amount = random.randint(50, 500)
        if specialty in ["Cardiology", "Oncology", "Neurology"]:
            base_amount *= random.randint(5, 20)
        elif specialty in ["Orthopedics"]:
            base_amount *= random.randint(2, 10)
            
        amount = round(base_amount + random.random() * 100, 2)
        
        procedure_code = f"CPT-{random.randint(10000, 99999)}"
        
        notes = f"Patient presented with symptoms of {diagnosis}. {status}."
        if status == "Denied":
            notes += f" Claim denied due to {denial_reason}."
            
        rows.append([
            claim_id, patient_id, doctor_id, doctor_name, specialty,
            diagnosis, procedure_code, claim_date, amount,
            status, denial_reason, notes
        ])
        
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"Successfully generated {NUM_CLAIMS} claims to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_claims()
