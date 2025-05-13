"""
validators/md_check.py
Perform lightweight validation on writer-LLM Markdown before parsing.

Dependencies
------------
pip install pyyaml markdown-it-py
"""

import re
import yaml

# ---------- 1. basic cleaning -------------------------------------------- #


def clean_markdown(raw: str) -> str:
    """
    Normalise whitespace, line-endings, and smart quotes.
    Returns the cleaned markdown string.
    """
    if not isinstance(raw, str):
        raise TypeError("Writer output must be str")

    # normalise CRLF → LF
    md = raw.replace("\r\n", "\n").replace("\r", "\n")

    # collapse Windows “smart quotes” → ASCII quotes
    smart = {
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "–": "-",
        "—": "-",
        " ": " ",  # NBSP → space
    }
    for k, v in smart.items():
        md = md.replace(k, v)

    # trim leading / trailing blank lines
    md = md.strip("\n")

    # collapse >2 consecutive blank lines
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md


# ---------- 2. schema validation ----------------------------------------- #

_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_H2_RE = re.compile(r"^##\s+", re.MULTILINE)
_HTML_RE = re.compile(r"<[a-zA-Z/][^>]*>")
_TICKS_RE = re.compile(r"```")

# REQUIRED_KEYS = {"doc_type", "style", "page_count", "name", "address", "phone", "email"}
REQUIRED_KEYS = {"doc_type", "style", "page_count"}


def validate_md_resume(md: str, max_tokens: int = 4000) -> tuple[bool, str]:
    """
    Checks the cleaned markdown against structural rules.

    Returns (is_valid, error_msg).  error_msg == "" when valid.
    """
    if len(md.split()) > max_tokens:
        return False, "token-count-overflow"

    # 1. front-matter block
    fm_match = _FRONT_RE.match(md)
    if not fm_match:
        return False, "missing-front-matter"
    try:
        meta = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        return False, "yaml-parse-error"
    if not REQUIRED_KEYS.issubset(meta.keys()):
        missing = REQUIRED_KEYS - meta.keys()
        return False, f"missing-yaml-keys: {', '.join(sorted(missing))}"

    # 2. at least one section heading
    if not _H2_RE.search(md):
        return False, "no-section-headings"

    # 3. disallow HTML tags
    if _HTML_RE.search(md):
        return False, "html-tag-found"

    # 4. disallow triple-back-tick code fences
    if _TICKS_RE.search(md):
        return False, "code-fence-found"

    # 5. real tab between left / right columns (look for H3 with a tab)
    if "\t" not in md.split("\n", 1)[1]:
        return False, "no-tab-character-found"

    return True, ""


# ---------- 3. convenience wrapper --------------------------------------- #


def clean_and_validate(raw: str) -> str:
    """
    Sanitise *and* validate.
    Raises ValueError with reason if invalid; returns cleaned markdown on success.
    """
    md = clean_markdown(raw)
    ok, err = validate_md_resume(md)
    if not ok:
        raise ValueError(f"writer markdown failed validation: {err}")
    return md
