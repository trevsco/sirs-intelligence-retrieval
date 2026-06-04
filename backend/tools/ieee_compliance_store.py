"""
ieee_compliance_store.py
-------------------------
Persists IEEE compliance results per document to a JSON file.
Stored at: backend/data/ieee_compliance_results.json

Each entry is keyed by doc_id:
{
    "abc-123": {
        "filename": "srs_document.pdf",
        "report": { ...compliance report dict... }
    }
}
"""

import json
from pathlib import Path
from loguru import logger

STORE_PATH = Path(__file__).parent.parent / "data" / "ieee_compliance_results.json"


def _load() -> dict:
    """Load all stored compliance results from JSON file."""
    if STORE_PATH.exists():
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load IEEE compliance store: {e}")
            return {}
    return {}


def _save(data: dict):
    """Write compliance results dict to JSON file."""
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_compliance(doc_id: str, filename: str, report: dict):
    """Save a compliance report for a specific document."""
    data = _load()
    data[doc_id] = {
        "filename": filename,
        "report": report
    }
    _save(data)
    logger.info(f"IEEE compliance result saved for doc_id: {doc_id} ({filename})")


def get_compliance(doc_id: str) -> dict | None:
    """Get compliance report for a specific document. Returns None if not found."""
    data = _load()
    return data.get(doc_id)


def delete_compliance(doc_id: str):
    """Remove compliance result when document is deleted."""
    data = _load()
    if doc_id in data:
        del data[doc_id]
        _save(data)
        logger.info(f"IEEE compliance result deleted for doc_id: {doc_id}")


def get_all_compliance() -> dict:
    """Return all stored compliance results."""
    return _load()