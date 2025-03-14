import re


def chunk_technical_skills(section_text: str) -> list[str]:
    """
    Break the 'TECHNICAL SKILLS' section into sub-chunks.
    Approach:
      1) Split the text into lines.
      2) For each line, detect if it follows the pattern '<Category>:'.
      3) If it does, treat that line as a sub-chunk that includes the
         category name plus the comma-separated skills.
      4) If it doesn't, you can either:
         - Append it to the last recognized category
         - Or treat it as a standalone chunk
    Returns a list of sub-chunks, each sub-chunk being the line or combined lines
    for that category.

    :param section_text: The entire text of the Technical Skills section
    :return: A list of sub-chunks (strings) for further processing
    """
    # Split into lines
    lines = section_text.split("\n")

    # A regex to detect lines that have a pattern like:
    # "Something: stuff, stuff, stuff"
    # We'll only check if there's a ':' somewhere in the line
    category_pattern = re.compile(r".+?:")

    sub_chunks: list[str] = []
    buffer_lines: list[str] = []
    current_category: str | None = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line looks like a new category
        if category_pattern.search(line):
            # If there was a category buffer in progress, store it
            if buffer_lines:
                # Join previous category lines
                sub_chunks.append("\n".join(buffer_lines).strip())
                buffer_lines = []

            # Start a new category buffer
            current_category = line  # e.g., "Programming Languages: Python, JavaScript"
            buffer_lines.append(current_category)
        else:
            # This line might be a continuation of the previous category
            if current_category is not None:
                buffer_lines.append(line)
            else:
                # If we have no current category, just store as its own chunk
                # or start a new chunk buffer
                sub_chunks.append(line)

    # If there's leftover buffer content, add it as a final chunk
    if buffer_lines:
        sub_chunks.append("\n".join(buffer_lines).strip())

    return sub_chunks
