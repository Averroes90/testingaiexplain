from typing import Dict, List, Tuple
import re


def parse_into_lines(resume_text: str) -> List[str]:
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


def extract_summary(lines: List[str]) -> Tuple[str, List[str]]:
    """
    Extract everything from the start of these lines up to (but not including)
    the first recognized heading as the 'SUMMARY'. Return the summary text
    and the leftover lines.

    :param lines: The lines AFTER removing name/contact lines.
    :return: (summary_text, remaining_lines)
    """
    # TODO: Implement logic that identifies where summary ends
    #       (e.g., first recognized heading line).
    pass


def find_section_headings(text: str) -> List[re.Match]:
    """
    Use a known set of regex patterns to locate headings (e.g., PROFESSIONAL EXPERIENCE, EDUCATION).

    :param text: The text after removing summary.
    :return: A list of regex match objects, each representing a found heading.
    """
    # TODO: Implement the regex-based search for headings.
    pass


def chunk_sections_by_headings(text: str, headings: List[re.Match]) -> Dict[str, str]:
    """
    Given the text (beyond summary) and a list of heading matches,
    slice out text chunks for each heading. Map them to a canonical heading name.

    :param text: The text to be chunked (excluding name, contact info, summary).
    :param headings: A list of matches from find_section_headings().
    :return: A dictionary {heading_name: text_chunk}
    """
    # TODO: Implement slicing logic from one heading to the next.
    pass


def extract_sections_from_text(resume_text: str) -> Dict[str, str]:
    """
    High-level orchestrator that:
      1) Splits text into lines
      2) Extracts name & contact
      3) Extracts summary
      4) Identifies headings
      5) Splits text by headings
      6) Collects all results (name, contact, summary, sections) into a single dict

    :param resume_text: The entire resume text.
    :return: A dictionary of:
             {
               'NAME': ...,
               'CONTACT_INFO': ...,
               'SUMMARY': ...,
               'PROFESSIONAL EXPERIENCE': ...,
               'EDUCATION': ...,
               ...
             }
    """
    # Step 1: Split into lines
    lines = parse_into_lines(resume_text)

    # Step 2: Extract name & contact
    name, contact_info, lines_after_contact = extract_name_and_contact_info(lines)

    # Step 3: Extract summary
    summary, lines_after_summary = extract_summary(lines_after_contact)

    # Convert the remaining lines to text for heading-based chunking
    remaining_text = "\n".join(lines_after_summary)

    # Step 4: Find headings
    heading_matches = find_section_headings(remaining_text)

    # Step 5: Chunk text by headings
    sections_map = chunk_sections_by_headings(remaining_text, heading_matches)

    # Step 6: Collect into one dictionary
    result = {"NAME": name, "CONTACT_INFO": contact_info, "SUMMARY": summary}
    result.update(sections_map)

    return result
