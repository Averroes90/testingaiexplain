import re

from networkx import tree_graph
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
    print("\n----- START OF CHUNK -----")
    print(resume_text)
    print("------ END OF CHUNK ------\n")
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


def extract_name_and_contact_info(lines: list[str]) -> tuple[str, str, list[str]]:
    """
    Extract the name (line 0) and contact info (line 1) from the list of lines.
    Then return the leftover lines after removing those two lines.

    For simplicity, we assume the first non-empty line is the candidate's name,
    and the second is the candidate's contact info. Everything else remains.

    :param lines: A list of lines (strings) from the resume.
    :return: (name, contact_info, remaining_lines)
    """
    # If there are no lines, return empty name/contact and empty leftover
    if not lines:
        return "", "", []

    # Extract name from first line
    name = lines[0]

    # If there's at least a second line, use it for contact info
    contact_info = lines[1] if len(lines) > 1 else ""

    # Remaining lines start from line 3 onward
    leftover_lines = lines[2:] if len(lines) > 2 else []

    return name, contact_info, leftover_lines


def extract_summary(lines: list[str]) -> tuple[str, list[str]]:
    """
    Extract everything from the start of these lines up to (but not including)
    the first recognized heading (found in synonym_dict). Return the summary text
    and the leftover lines.

    :param lines: The lines AFTER removing name/contact lines.
    :param synonym_dict: A dict mapping lowercased synonyms -> canonical heading names
    :return: (summary_text, remaining_lines)
    """

    synonym_dict = load_secction_headings()

    summary_lines: list[str] = []
    leftover_index = len(lines)  # default if we never find a heading

    for i, line in enumerate(lines):
        # Check if the line matches any known synonym (case-insensitive)
        line_lower = line.lower()
        if line_lower in synonym_dict:
            leftover_index = i
            break
        summary_lines.append(line)

    leftover_lines = lines[leftover_index:]
    summary_text = "\n".join(summary_lines)
    return summary_text, leftover_lines


def find_section_headings(text: str) -> list[re.Match]:
    """
    Use the synonym -> canonical dict to locate headings in 'text'.

    Implementation:
      1) We'll build a single pattern that matches any key in synonym_dict (case-insensitive).
      2) Use multiline mode so ^/$ anchor to each line.
      3) Return a list of re.Match objects where each match indicates a heading line.

    :param text: The text in which to find headings (beyond summary).
    :param synonym_dict: A dict mapping lowercased synonyms -> canonical heading names.
    :return: A list of re.Match objects. Each match indicates the line that matched a heading synonym.
    """

    synonym_dict = load_secction_headings()

    # 1) Extract all synonyms from the dictionary
    all_synonyms = list(
        synonym_dict.keys()
    )  # keys are already lowercased in the dictionary

    # 2) Build the pattern to match any of these synonyms on a line by itself
    synonyms_pattern = "|".join(re.escape(s) for s in all_synonyms)
    pattern = re.compile(
        rf"^(?:{synonyms_pattern})$", flags=re.IGNORECASE | re.MULTILINE
    )

    # 3) Find and return all matches
    matches = list(pattern.finditer(text))
    return matches


def chunk_sections_by_headings(lines: list[str]) -> dict[str, str]:
    """
    Given a list of lines (excluding name/contact info/summary lines)
    and a path to a headings JSON file, this function:

      1) Loads the synonyms -> canonical headings from the JSON.
      2) Iterates over each line in 'lines'.
      3) When a line matches one of the known heading synonyms (case-insensitive),
         we start a new section under that canonical heading name.
      4) Accumulates lines until the next heading, at which point those lines
         form the text for that heading.

    :param lines: The lines to be chunked (excluding name, contact info, summary).
    :param headings_json_path: Path to the JSON file containing heading synonyms.
    :return: A dictionary {canonical_heading: text_chunk}, where text_chunk
             is joined from the lines belonging to that heading.
    """
    # Load the dictionary of {lowercased synonym: canonical heading}
    synonym_dict = load_secction_headings()

    sections: dict[str, str] = {}

    current_heading = None
    chunk_buffer: list[str] = []

    for line in lines:
        line_lower = line.lower()

        # If this line matches a known synonym, we start a new heading section
        if line_lower in synonym_dict:
            # If we were building up a chunk for the previous heading, store it
            if current_heading:
                sections[current_heading] = "\n".join(chunk_buffer).strip()

            # Switch current heading to the canonical name
            current_heading = synonym_dict[line_lower]
            chunk_buffer = []
        else:
            # This line belongs to the current heading (if any)
            chunk_buffer.append(line)

    # If there's leftover text for the last heading, store it
    if current_heading:
        sections[current_heading] = "\n".join(chunk_buffer).strip()

    return sections


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


# def is_merged_grammatical(text: str, nlp) -> bool:
#     """
#     Checks whether the merged text is a grammatically valid sentence,
#     allowing an initial bullet (NFP), but rejecting other structural noise.
#     """
#     try:
#         doc = nlp(text)
#         if not doc.sentences:
#             return False

#         for sent in doc.sentences:
#             if not sent.constituency:
#                 continue

#             tree_str = str(sent.constituency).strip()

#             # Ensure top-level structure is a sentence
#             if (
#                 not tree_str.startswith("(ROOT (S")
#                 and not tree_str.startswith("(ROOT (SINV")
#                 and not tree_str.startswith("(ROOT (SBAR")
#             ):
#                 # If not a sentence root, and sentence is embedded inside a noun phrase, reject
#                 if re.search(r"\(NP\s+\(S[\s\)]", tree_str):
#                     return False

#             # ✅ ALLOW: One NFP at very beginning of tree (before any words)
#             # ❌ REJECT: Any NFP/ADD/EMAIL/URL that appears later
#             nfp_index = tree_str.find("NFP")
#             if nfp_index != -1:
#                 # Check if it's the very first non-whitespace thing (root allowance)
#                 first_occurrence = re.search(r"\(NFP\b", tree_str)
#                 if first_occurrence and first_occurrence.start() > 30:  # ROOT + (S ...)
#                     return False  # NFP not at the start

#             # Block structural noise elsewhere
#             if any(tag in tree_str for tag in ["ADD", "EMAIL", "URL"]):
#                 return False

#         return True

#     except Exception:
#         return False


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
