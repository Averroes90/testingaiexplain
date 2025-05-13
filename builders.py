# app/builders.py
import io, uuid, os
from typing import Any
from docxtpl import DocxTemplate
from docx.shared import Cm
import redis
from pathlib import Path
import uuid
import time
import secrets
from settings import STORAGE_DIR, redis_cli

# 1.  build_docx ----------------------------------------------------------- #
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")


def build_docx(ctx: dict[str, Any]) -> bytes:
    """
    Render a DOCX using the .dotx template chosen by doc_type + style.
    """
    template_name = f"{ctx['doc_type']}_{ctx['style']}.dotx"
    tpl_path = os.path.join(TEMPLATE_DIR, template_name)
    doc = DocxTemplate(tpl_path)
    doc.render(ctx)

    # Hard page-limit enforcement (crude but effective)
    if ctx["page_count"] == 1:
        for sec in doc.docx.sections[1:]:
            doc.docx.element.body.remove(sec._sectPr)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.read()


# 2.  Redis staging -------------------------------------------------------- #


def _doc_dir(doc_id: str) -> Path:
    d = STORAGE_DIR / doc_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_version(doc_id: str, version: int, buf: bytes) -> Path:
    path = _doc_dir(doc_id) / f"v{version}.docx"
    path.write_bytes(buf)
    return path


def _init_redis_meta(doc_id: str, version: int, relpath: str) -> None:
    ds_key = f"{doc_id}-{version}"
    jwt_key = secrets.token_hex(16)  # optional; skip if JWT_DISABLED
    redis_cli.hset(
        f"doc:{doc_id}",
        mapping={
            "version": version,
            "relpath": relpath,
            "dsKey": ds_key,
            "jwtKey": jwt_key,
            "title": "",  # fill later if you have one
            "updatedAt": int(time.time()),
        },
    )


def persist_new_doc(buf: bytes) -> str:
    """
    1. Generate a UUID docId
    2. Write v1.docx to disk
    3. Seed Redis metadata
    4. Return the docId
    """
    doc_id = uuid.uuid4().hex
    version = 1
    path = _write_version(doc_id, version, buf)
    _init_redis_meta(doc_id, version, str(path.relative_to(STORAGE_DIR.parent)))
    return doc_id


def stage_docx(buf: bytes, ttl_sec: int = 3600) -> str:
    """
    Put DOCX bytes into Redis, return the cache key.
    """
    doc_id = f"doc:{uuid.uuid4().hex}.docx"
    redis_cli.set(doc_id, buf, ex=ttl_sec)
    return doc_id


def fetch_docx(doc_id: str) -> bytes | None:
    return redis_cli.get(doc_id)
