import re
import utils


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

    return filtered_lines


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
