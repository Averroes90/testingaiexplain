"""
validators/patch_guard.py
Step 6 – Pydantic schema validation + optional guard-LLM patch.

Dependencies
------------
pip install pydantic==2.*  deepmerge  (guard_llm client of your choice)
"""

from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationError, NonNegativeInt
from copy import deepcopy
import deepmerge  # pip install deepmerge


# --------------------------------------------------------------------------- #
# 1.  Pydantic schema (covers résumé *and* cover-letter)                      #
# --------------------------------------------------------------------------- #


class BulletItem(BaseModel):
    text: str = Field(..., min_length=2, max_length=500)


class SubLine(BaseModel):
    sub_left: Optional[str] = None
    sub_right: Optional[str] = None
    bullets: list[BulletItem] = Field(..., min_items=1)


class OrgItem(SubLine):
    org_left: Optional[str] = None
    org_right: Optional[str] = None


class Section(BaseModel):
    title: str = Field(..., min_length=3, max_length=40)
    items: list[OrgItem] = Field(..., min_items=1)


class ResumeDoc(BaseModel):
    # YAML meta
    doc_type: str
    style: str
    page_count: NonNegativeInt
    name: str
    address: str
    phone: str
    email: str
    linkedin: Optional[str] = None

    # body
    sections: list[Section] = Field(..., min_items=1)


# --------------------------------------------------------------------------- #
# 2.  Validation + missing-field detector                                     #
# --------------------------------------------------------------------------- #


def validate_context(ctx: dict[str, Any]) -> ResumeDoc | None:
    """
    Returns parsed ResumeDoc or None if validation fails.
    """
    try:
        return ResumeDoc.model_validate(ctx)
    except ValidationError:
        return None


def find_missing(ctx: dict[str, Any]) -> list[str]:
    """
    Collect paths that violate bullet count or missing left/right fields.
    """
    missing: list[str] = []
    for si, sec in enumerate(ctx.get("sections", [])):
        for ii, item in enumerate(sec.get("items", [])):
            path = f"sections[{si}].items[{ii}]"
            if not item.get("bullets"):
                missing.append(f"{path}.bullets")
            if ctx["doc_type"] == "resume":
                if not item.get("org_left"):
                    missing.append(f"{path}.org_left")
            # add your own conditions here if needed
    return missing


# --------------------------------------------------------------------------- #
# 3.  Guard-LLM patch call (stub implementation)                              #
# --------------------------------------------------------------------------- #


def call_guard_llm(missing_ctx: dict[str, Any]) -> dict[str, Any]:
    """
    Call a very small LLM with the partial structure that needs completion.
    Must return JSON with identical keys/shape, filling only missing strings /
    bullets.  *Stubbed here* – integrate your SDK.
    """
    prompt = (
        "Fill in the missing fields (empty strings or empty bullet lists) "
        "in the supplied JSON. Keep keys identical. "
        "Return valid JSON only.\n\n"
        "JSON:\n" + repr(missing_ctx)
    )
    # --- replace the block below with your async or sync LLM call -----------
    # llm_response = guard_llm.run(prompt=prompt)
    # patch = json.loads(llm_response)
    # For demo purposes, we fake a minimal patch:
    patch = deepcopy(missing_ctx)
    patch["name"] = patch.get("name") or "Jane Doe"
    for sec in patch.get("sections", []):
        for item in sec.get("items", []):
            if not item.get("bullets"):
                item["bullets"] = [{"text": "Placeholder achievement."}]
    return patch


# --------------------------------------------------------------------------- #
# 4.  Public helper – validate-or-patch-and-validate                          #
# --------------------------------------------------------------------------- #


def ensure_valid(ctx: dict[str, Any], allow_llm_patch: bool = True) -> ResumeDoc:
    """
    1. Try to validate the parsed context.
    2. If it fails and allow_llm_patch=True, send only missing parts to guard-LLM,
       merge patch, and validate again.
    3. If still invalid, raise ValidationError.
    """
    doc = validate_context(ctx)
    if doc:
        return doc

    if not allow_llm_patch:
        raise ValidationError("Context failed validation and LLM patch disabled")

    # Build lightweight missing-only dict
    missing_paths = find_missing(ctx)
    if not missing_paths:
        raise ValidationError("Context invalid for unknown reasons")

    # Assemble sparse dict for LLM
    sparse: dict[str, Any] = {}
    for path in missing_paths:
        deepmerge.always_merger.set(sparse, path, "")

    # patch via LLM
    patch = call_guard_llm(sparse)
    ctx_patched = deepmerge.always_merger.merge(deepcopy(ctx), patch)

    # re-validate
    doc = validate_context(ctx_patched)
    if not doc:
        raise ValidationError("Context remains invalid after LLM patch")
    return doc
