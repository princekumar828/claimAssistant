import pytest
from etl.processor import ClaimProcessor

def test_normalization():
    processor = ClaimProcessor()
    text = "  HELLO   World  "
    assert processor.normalize_text(text) == "hello world"

def test_document_creation():
    processor = ClaimProcessor()
    record = {
        "claim_id": "123",
        "patient_id": "P1",
        "doctor_name": "Dr. No",
        "specialty": "Spy",
        "diagnosis": "Deadly",
        "procedure_code": "007",
        "claim_date": "2020-01-01",
        "amount": "100.00",
        "status": "Denied",
        "denial_reason": "Secret",
        "notes": "None"
    }
    doc = processor.create_search_document(record)
    assert "claim 123" in doc
    assert "status is denied" in doc
    assert "secret" in doc

def test_processing():
    processor = ClaimProcessor()
    records = [{"claim_id": "1", "status": "A"}, {"claim_id": "2", "status": "B"}]
    docs = processor.process_records(records)
    assert len(docs) == 2
    assert docs[0]["id"].startswith("1_")
