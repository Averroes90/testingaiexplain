# seed_placeholder.py  (lives anywhere in your backend codebase)
import time, secrets, redis
from pathlib import Path
from docx import Document
from settings import redis_cli


DOC_ID = "placeholder"
STORE_PATH = Path("storage/docs/placeholder")
DOC_PATH = STORE_PATH / "v1.docx"


def ensure_placeholder():
    """Create placeholder.docx on disk and a matching Redis hash."""
    if not DOC_PATH.exists():
        STORE_PATH.mkdir(parents=True, exist_ok=True)
        doc = Document()
        doc.add_paragraph("Generate a résumé to begin editing.")
        doc.save(DOC_PATH)

    if not redis_cli.exists(f"doc:{DOC_ID}"):
        redis_cli.hset(
            f"doc:{DOC_ID}",
            mapping={
                "title": "Placeholder Résumé",
                "version": 1,
                "relpath": str(DOC_PATH),
                "dsKey": f"{DOC_ID}-1",
                "jwtKey": secrets.token_hex(16),
                "updatedAt": int(time.time()),
            },
        )
