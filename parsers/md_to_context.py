"""
parsers/md_to_context.py
Convert cleaned Markdown (plus YAML front-matter) into the JSON
structure required by docx_builder.

Dependencies
------------
pip install markdown-it-py pyyaml
"""

import re
import yaml
from typing import Any

from markdown_it import MarkdownIt

# --------------------------------------------------------------------------- #
# 1. Helpers
# --------------------------------------------------------------------------- #

_H2_RE = re.compile(r"^##\s+(.*)")
_H3_RE = re.compile(r"^###\s+(.*)")
_H4_RE = re.compile(r"^####\s+(.*)")
_BULLET_RE = re.compile(r"^- (.*)")


def _split_tab(line: str) -> tuple[str, str]:
    """Split at the first real tab char; return (left, right)."""
    if "\t" in line:
        left, right = line.split("\t", 1)
        return left.strip(), right.strip()
    return line.strip(), ""


# --------------------------------------------------------------------------- #
# 2. Main parser
# --------------------------------------------------------------------------- #


def md_to_context(md_src: str) -> dict[str, Any]:
    """
    Parameters
    ----------
    md_src : str
        Cleaned markdown from the writer LLM, including YAML front-matter.

    Returns
    -------
    context : dict
        Dict ready for docxtpl.render().
    """
    # ---------- 2.1  separate YAML front-matter ---------------------------- #
    if not md_src.startswith("---"):
        raise ValueError("front-matter missing at top of markdown")

    fm_end = md_src.find("\n---", 3)
    if fm_end == -1:
        raise ValueError("front-matter not closed with second ---")

    meta = yaml.safe_load(md_src[3:fm_end])
    body = md_src[fm_end + 4 :].lstrip("\n")  # skip the trailing \n after ---

    doc_type = meta.get("doc_type", "").lower()
    if doc_type not in {"resume", "cover_letter"}:
        raise ValueError("doc_type must be 'resume' or 'cover_letter'")

    # ---------- 2.2  init markdown parser ---------------------------------- #
    md = MarkdownIt("commonmark")
    lines = body.splitlines()

    sections: list[dict[str, Any]] = []
    current_sec = None
    current_item = None

    def flush_item():
        nonlocal current_item
        if current_item:
            current_sec["items"].append(current_item)
            current_item = None

    # ---------- 2.3  iterate line by line ---------------------------------- #
    for raw in lines:
        line = raw.rstrip()

        # --- cover letter path: no H2 headings ----------------------------- #
        if doc_type == "cover_letter":
            # Accumulate paragraphs into one section called COVER LETTER
            if not sections:
                sections.append(
                    {
                        "title": "COVER LETTER",
                        "items": [
                            {
                                "org_left": "",
                                "org_right": "",
                                "sub_left": "",
                                "sub_right": "",
                                "bullets": [],
                            }
                        ],
                    }
                )
            item = sections[0]["items"][0]
            if line.startswith("- "):
                item["bullets"].append(line[2:].strip())
            elif line:
                # store as a paragraph bullet for simplicity
                item["bullets"].append(line.strip())
            continue

        # --- résumé path --------------------------------------------------- #
        m = _H2_RE.match(line)
        if m:
            # new section
            flush_item()
            current_sec = {"title": m.group(1).strip(), "items": []}
            sections.append(current_sec)
            continue

        m = _H3_RE.match(line)
        if m and current_sec:
            flush_item()
            left, right = _split_tab(m.group(1))
            current_item = {
                "org_left": left,
                "org_right": right,
                "sub_left": "",
                "sub_right": "",
                "bullets": [],
            }
            continue

        m = _H4_RE.match(line)
        if m and current_item:
            left, right = _split_tab(m.group(1))
            current_item["sub_left"] = left
            current_item["sub_right"] = right
            continue

        m = _BULLET_RE.match(line)
        if m and current_item:
            current_item["bullets"].append(m.group(1).strip())
            continue

        # ignore blank lines and any stray text

    flush_item()  # flush last item

    if not sections:
        raise ValueError("no sections parsed; check writer output")

    # ---------- 2.4  assemble final context ------------------------------- #
    context: dict[str, Any] = {
        **meta,
        "sections": sections,
    }
    return context
