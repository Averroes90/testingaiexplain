# backend/models/writer_output.py  (Pydantic v2)

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DocType(str, Enum):
    resume = "resume"
    cover_letter = "cover_letter"


class Meta(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    doc_type: DocType
    style: str = Field(..., min_length=3, max_length=30)
    page_count: int = Field(..., gt=0, lt=5)


class WriterOutput(BaseModel):
    meta: Meta
    content: str = Field(..., max_length=40_000)

    # ── v2-style validator ────────────────────────────────
    @field_validator("content")
    def ensure_markdown(cls, v: str) -> str:
        if "<" in v and ">" in v:
            raise ValueError("HTML tags are not allowed; use Markdown only.")
        return v


# 1) Define a Pydantic model that matches the expected input payload
class GenerateRequest(BaseModel):
    url: str
    doc_type: list[str]
    style: list[str]
    page_count: list[int]


class DSCallback(BaseModel):
    status: int
    url: str  # DS provides this when status ∈ {2,6}
