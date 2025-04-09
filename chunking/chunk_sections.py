import re
import utils
from nlp.zsc import classify_line_zsc, load_zsc_model
from nlp.ner import extract_ner, load_ner_model


def load_secction_headings() -> dict[str, str]:
    headings_json_path = "config/labels.json"
    synonym_dict: dict[str, str] = {}
    full_synonym_dict = utils.load_flat_labels(headings_json_path)

    for synonym_lower, meta in full_synonym_dict.items():
        if meta["label_type"] == "SECTION_HEADING":
            # map the lowercased synonym to the canonical heading
            synonym_dict[synonym_lower] = meta["canonical_label"]
    return synonym_dict


def parse_into_lines(resume_text: str) -> list[str]:
    """
    Split the resume text into a list of non-empty lines, stripping leading
    and trailing whitespace. Also removes any header/footer lines
    that match known patterns (e.g., lines containing 'Page ... of ... <digits>').

    :param resume_text: Entire resume text.
    :return: List of lines (strings) with no empty entries or headers/footers.
    """

    # A broad pattern: if a line contains the word "page" and "of"
    # and at least one digit, we'll consider it a header/footer.
    # Example matches:
    #  - "Page 1 of 2"
    #  - "Some text Page   2  of   5 something"
    #  - "Page  of 12"
    # print("\n----- START OF CHUNK -----")
    # print(resume_text)
    # print("------ END OF CHUNK ------\n")
    header_footer_pattern = re.compile(r"(?i).*page.*of.*\d+.*")

    def is_header_or_footer(line: str) -> bool:
        # Check the pattern
        if header_footer_pattern.match(line):
            return True

        # Add any other custom checks here if needed, e.g. "Confidential"
        return False

    # 1. Split on newlines
    raw_lines = resume_text.split("\n")

    # 2. Strip and filter out blank lines
    stripped_lines = [line.strip() for line in raw_lines if line.strip()]

    # 3. Skip lines recognized as headers/footers
    filtered_lines = [line for line in stripped_lines if not is_header_or_footer(line)]

    normalize_space_lines = normalize_spaces(filtered_lines)
    # merge_lines = chunk_merge(normalize_space_lines, nlp)
    # return normalize_space_lines
    return normalize_space_lines


def normalize_spaces(lines: list[str]) -> list[str]:
    """
    Converts any sequence of 2 or more consecutive spaces
    into a single space, for each line in 'lines'.

    :param lines: List of lines after chunk merging (where we no longer need spacing data).
    :return: A new list of lines with spurious spaces removed.
    """
    normalized = []
    for line in lines:
        # Convert multiple spaces into 1
        # You could also consider tabs, etc.
        line_clean = re.sub(r"\s{2,}", " ", line)
        # Optionally trim again if you want
        line_clean = line_clean.strip()
        normalized.append(line_clean)
    return normalized


BULLET_REGEX_ANYWHERE = re.compile(r"(?<!\w)[\u2022\*\+\-‣▪∙‾·](?!\w)")


def contains_bullet(text: str) -> bool:
    """
    Returns True if the line contains a bullet-like symbol,
    but ignores hyphens inside words (e.g., 'hands-on').
    """
    return bool(BULLET_REGEX_ANYWHERE.search(text))


CONTACT_PATTERNS = [
    r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b",  # Email
    r"\b(?:https?:\/\/)?(?:www\.)?\w+\.\w{2,}(\/\S*)?\b",  # URLs/domains
    r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b",  # Phone numbers
    r"\blinkedin\.com\/\S+\b",  # LinkedIn
    r"\bgithub\.com\/\S+\b",  # GitHub
    r"\btwitter\.com\/\S+\b",  # Twitter
    r"@\w{2,}",  # Handles
]

contact_info_regex = re.compile("|".join(CONTACT_PATTERNS), re.IGNORECASE)


def contains_contact_info(text: str) -> bool:
    """
    Returns True if the text contains email, URL, phone number,
    or common social profile/contact indicators.
    """
    return bool(contact_info_regex.search(text))


def is_visually_separated(
    line_a: str, line_b: str, max_line_length: int, gap_ratio: float = 0.15
) -> bool:
    """
    Returns True if line_a ends with a large visual gap, and line_b begins with a short word,
    suggesting visual separation in layout (e.g., like justified resume formats).

    :param line_a: The first line to evaluate (typically the current line).
    :param line_b: The following line.
    :param max_line_length: The length of the longest line in the document.
    :param gap_ratio: The threshold proportion of visual gap (e.g., 0.15 = 15% of max).
    """
    line_a = line_a.rstrip()
    visual_gap = max_line_length - len(line_a)

    # Extract first word of line B
    first_word_length = len(line_b.strip().split()[0]) if line_b.strip() else 0

    # If visual gap at end of A is greater than first word of B and exceeds ratio
    return visual_gap > first_word_length and visual_gap / max_line_length >= gap_ratio


CONJUNCTIONS = {
    "and",
    "or",
    "but",
    "so",
    "yet",
    "because",
    "although",
    "though",
    "while",
    "nor",
    "for",
    "with",
    "as",
    "if",
    "when",
    "after",
    "before",
    "until",
    "to",
    "from",
    "however",
    "moreover",
    "furthermore",
    "therefore",
    "thus",
    "meanwhile",
    "additionally",
    "also",
    "besides",
    "then",
    "in",
    "on",
}


def ends_with_conjunction(text: str) -> bool:
    """
    Returns True if the last word in the text is a conjunction, suggesting continuation.
    """
    words = text.strip().lower().rstrip(".").split()
    return bool(words) and words[-1] in CONJUNCTIONS


def starts_with_conjunction(text: str) -> bool:
    """
    Returns True if the first word in the text is a conjunction, suggesting it might be a continuation.
    """
    words = text.strip().lower().split()
    return bool(words) and words[0] in CONJUNCTIONS


zsc_pipeline = load_zsc_model()
ner_pipeline = load_ner_model()


def generate_line_features(lines):
    max_line_length = max(len(line) for line in lines)
    table = []

    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        zsc_results = classify_line_zsc(line, zsc_pipeline)
        top_zsc = extract_top_zsc_label(zsc_results)
        features = {
            "line": line,
            "is_visually_separated": is_visually_separated(
                line, next_line, max_line_length
            ),
            "contains_bullet": contains_bullet(line),
            "contains_contact_info": contains_contact_info(line),
            "ends_with_conjunction": ends_with_conjunction(line),
            "starts_with_conjunction": starts_with_conjunction(line),
            "zero_shot_classification": top_zsc,  # Returns label or top score label
            "named_entity_recognition": extract_ner(
                line, ner_pipeline
            ),  # Returns list of entities or label spans
            "is_section_header": matching_section_header(
                line
            ),  # Could be rule or zsc-based
        }

        table.append(features)

    return table


def matching_section_header(line: str) -> str | None:
    """
    Checks if the line matches any section header label or synonym.

    :param line: The text line to evaluate.
    :return: The canonical label if matched; otherwise, None.
    """
    headings_json_path = "config/resume_headers.json"
    flat_map = utils.load_flat_labels(headings_json_path)

    normalized_line = line.strip().lower()

    # Check if the line matches any label or synonym
    if normalized_line in flat_map:
        return flat_map[normalized_line]["canonical_label"]

    return None


def extract_top_zsc_label(
    zsc_results: list[dict[str, float]],
) -> dict[str, float | None]:
    """
    Extracts the top label and its score from the full zero-shot classification result.

    :param zsc_results: Output from classify_line_zsc(), a sorted list of dicts.
    :return: Dict with keys 'label' and 'score'. None values if input is empty.
    """
    if zsc_results:
        return {"label": zsc_results[0]["label"], "score": zsc_results[0]["score"]}
    else:
        return {"label": None, "score": None}
