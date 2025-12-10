import csv
import re
from typing import List, Dict, Any

class ClaimProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Loads CSV data into a list of dictionaries."""
        records = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found.")
        return records

    def normalize_text(self, text: str) -> str:
        """Simple text normalization."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def create_search_document(self, record: Dict[str, Any]) -> str:
        """
        Converts a claim record into a descriptive string for embedding.
        """
        # Format: "Claim [ID] for Patient [ID] on [Date]. Status: [Status]. Diagnosis: [Diagnosis]. Amount: $[Amount]. Doctor: [Doctor] ([Specialty]). Reason: [Reason]. Notes: [Notes]"
        
        status_text = f"Status is {record.get('status', 'Unknown')}."
        if record.get('denial_reason'):
            status_text += f" Denial reason: {record.get('denial_reason')}."
            
        doc_text = (
            f"Claim {record.get('claim_id')} submitted on {record.get('claim_date')}. "
            f"Patient ID: {record.get('patient_id')}. "
            f"Doctor: {record.get('doctor_name')} ({record.get('specialty')}). "
            f"Diagnosis: {record.get('diagnosis')}. "
            f"Procedure Code: {record.get('procedure_code')}. "
            f"Amount: ${record.get('amount')}. "
            f"{status_text} "
            f"Notes: {record.get('notes')}"
        )
        return self.normalize_text(doc_text)

    def process_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes records into documents for the vector store.
        Returns a list of dicts with 'id', 'text', 'metadata'.
        """
        processed_docs = []
        for record in records:
            text = self.create_search_document(record)
            
            # Simple chunking if text is too long (unlikely for this data, but good practice)
            # This is a naive split; real production code might use nltk or langchain
            if len(text) > self.chunk_size:
                chunks = [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
            else:
                chunks = [text]
                
            for i, chunk in enumerate(chunks):
                processed_docs.append({
                    "id": f"{record['claim_id']}_{i}",
                    "text": chunk,
                    "metadata": record 
                })
        return processed_docs
