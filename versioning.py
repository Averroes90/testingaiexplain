# versioning.py
from pathlib import Path

from settings import STORAGE_DIR  # imported from settings.py


def _doc_dir(doc_id: str) -> Path:
    d = STORAGE_DIR / doc_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_version(doc_id: str, version: int, buf: bytes) -> Path:
    """
    Write DOCX bytes to storage/docs/<docId>/v{n}.docx and return the Path.
    """
    path = _doc_dir(doc_id) / f"v{version}.docx"
    path.write_bytes(buf)
    return path
