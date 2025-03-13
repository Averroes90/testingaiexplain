import re
from typing import Dict, List, Any


import re
from typing import Dict


def extract_sections_from_text(resume_text: str) -> Dict[str, str]:
    """
    Given the full resume text, this function:
      1) Extracts the first line as 'NAME'.
      2) Extracts the second line as 'CONTACT_INFO'.
      3) Treats everything from line 3 onward until the first recognized heading
         as 'SUMMARY'.
      4) Splits the rest of the text by recognized headings
         (e.g., PROFESSIONAL EXPERIENCE, EDUCATION, etc.)
      5) Returns a dictionary {section_name: section_text}.

    :param resume_text: The entire resume in plain text.
    :return: A dictionary mapping canonical section names to the raw text.
    """

    # 1. Convert the full text into a list of lines, stripping empty ones.
    lines = resume_text.split("\n")
    lines = [line.strip() for line in lines if line.strip()]  # remove blank lines

    if not lines:
        # If there's no text at all, return an empty dictionary
        return {}

    # 2. Extract name (line 0) and contact info (line 1) if available
    #    We'll store them under specific keys in our final output dict.
    sections = {}
    sections["NAME"] = lines[0]

    if len(lines) > 1:
        sections["CONTACT_INFO"] = lines[1]
    else:
        sections["CONTACT_INFO"] = ""

    # We will treat everything from line[2] onward as the main body
    main_body_lines = lines[2:] if len(lines) > 2 else []
    main_body_text = "\n".join(main_body_lines)

    # 3. Define the canonical headings and possible variations or synonyms.
    heading_synonyms = {
        r"(?i)PROFESSIONAL EXPERIENCE": "PROFESSIONAL EXPERIENCE",
        r"(?i)TECHNICAL SKILLS": "TECHNICAL SKILLS",
        r"(?i)SKILLS": "TECHNICAL SKILLS",  # if someone wrote just 'SKILLS'
        r"(?i)EDUCATION": "EDUCATION",
        r"(?i)SELECTED TECHNICAL PROJECTS": "PROJECTS",
        r"(?i)PROJECTS": "PROJECTS",
        r"(?i)ADDITIONAL INFORMATION": "ADDITIONAL INFORMATION",
    }

    # Combine synonyms into one big OR'ed pattern.
    # We'll use capturing groups so we can see which heading matched.
    big_pattern = "|".join(f"({syn})" for syn in heading_synonyms.keys())
    heading_regex = re.compile(big_pattern)

    # 4. Find all heading matches in the main body text
    matches = list(heading_regex.finditer(main_body_text))

    # If no headings are found, everything in main_body_text is SUMMARY
    if not matches:
        sections["SUMMARY"] = main_body_text.strip()
        return sections

    # Otherwise, the text from start of main_body_text up to the first heading is SUMMARY.
    first_heading_start = matches[0].start()
    summary_text = main_body_text[:first_heading_start].strip()
    sections["SUMMARY"] = summary_text

    # We'll add a pseudo-match to handle capturing text after the last heading
    pseudo_match = type("PseudoMatch", (object,), {})()
    pseudo_match.start = lambda: len(main_body_text)
    matches.append(pseudo_match)

    # 5. Iterate through heading matches to slice out each section
    for i in range(len(matches) - 1):
        match = matches[i]
        heading_str = match.group(0)  # the actual text that matched
        heading_start = match.start()
        heading_end = match.end()

        # Map heading text to canonical heading name
        canonical_name = None
        for pattern, cname in heading_synonyms.items():
            if re.match(pattern, heading_str, flags=re.IGNORECASE):
                canonical_name = cname
                break

        # Next heading's start
        next_heading_start = matches[i + 1].start()

        # The chunk of text for this section
        section_text = main_body_text[heading_end:next_heading_start].strip()

        if canonical_name:
            sections[canonical_name] = section_text
        else:
            # If somehow we didn't get a canonical name, store it under the matched heading
            sections[heading_str.upper()] = section_text

    return sections


def parse_professional_experience(experience_text: str) -> List[Dict[str, Any]]:
    """
    Given the text chunk corresponding to 'PROFESSIONAL EXPERIENCE',
    split it by roles/sub-entries. For example, you have Google LLC
    under which there is T/ Program Manager (2019-2023), then there's
    an MBA Intern role, etc.

    :param experience_text: All text under PROFESSIONAL EXPERIENCE
    :return: A list of dictionaries, each representing one role or sub-entry, e.g.
             [
               {
                 "company": "Google LLC",
                 "role": "Product Operations T/ Program Manager",
                 "dates": "2019-2023",
                 "location": "Mountain View, CA",
                 "bullets": [
                     "Managed overseas team of data scientists...",
                     ...
                 ]
               },
               ...
             ]
    """
    # TODO: Implement your splitting and regex capture logic here.
    #       You might:
    #       - Identify lines that look like "Google LLC 2018-2023"
    #       - Then further parse sub-roles by scanning for role, date, location
    #       - Collect bullet points until the next role starts.

    experience_entries = []
    # [Your code goes here...]

    return experience_entries


def parse_education_section(education_text: str) -> List[Dict[str, Any]]:
    """
    Given the text chunk for EDUCATION, split it by each institution/degree.

    :param education_text: All text under EDUCATION
    :return: A list of dictionaries, e.g.
             [
               {
                 "institution": "Columbia University",
                 "degree": "Certificate in AI",
                 "graduation_date": "June 2024",
                 "bullets": [
                     "Projects: ...",
                     "Key skills: ..."
                 ]
               },
               ...
             ]
    """
    # TODO: Implement your logic for splitting institutions and extracting data.

    education_entries = []
    # [Your code goes here...]

    return education_entries


def parse_skills_section(skills_text: str) -> Dict[str, List[str]]:
    """
    Parse the 'TECHNICAL SKILLS' section. Typically, you might have
    bullet points or semi-colon separated categories (Programming Languages, etc.).

    :param skills_text: All text under TECHNICAL SKILLS
    :return: A dictionary of skill_category -> list of skills, e.g.
             {
               "Programming Languages": ["Python", "JavaScript", "SQL", "C"],
               "Machine Learning": ["TensorFlow", "Keras", "Scikit-learn", "PyTorch"],
               ...
             }
    """
    # TODO: Implement splitting by bullet points, or parse lines that start with "•"
    #       Then map each line to a category, if present.

    skills_data = {}
    # [Your code goes here...]

    return skills_data


def parse_projects_section(projects_text: str) -> List[Dict[str, Any]]:
    """
    Parse a 'PROJECTS' or 'SELECTED TECHNICAL PROJECTS' section into a list of projects.

    :param projects_text: Text chunk under 'PROJECTS'
    :return: A list of project dictionaries, e.g.
             [
               {
                 "title": "Auto Transcribe and Translate",
                 "date_range": "Mar 2024 - present",
                 "technologies": ["Python", "NLP", "spaCy", ...],
                 "description": [
                     "Developed an advanced tool...",
                     "Achieved 5% WER..."
                 ]
               },
               ...
             ]
    """
    # TODO: You can look for lines that mention the project name + date range.
    #       Then parse bullet points or lines under that heading.

    projects_list = []
    # [Your code goes here...]

    return projects_list


def parse_additional_info(additional_text: str) -> Dict[str, Any]:
    """
    Parse any 'ADDITIONAL INFORMATION' or 'ADDITIONAL' section, which might
    include languages, personal interests, etc.

    :param additional_text: Text chunk under 'ADDITIONAL INFORMATION'
    :return: A dictionary with fields like:
             {
               "citizenship": ["United States", "Jordan"],
               "languages": ["English", "Arabic", "Turkish (basic)"],
               "interests": ["soccer", "mountain biking"]
             }
    """
    additional_data = {}
    # [Your code goes here...]

    return additional_data


def chunk_resume_into_subgroups(resume_text: str) -> Dict[str, Any]:
    """
    High-level function that orchestrates:
      1) Extracting major sections from the resume text
      2) Parsing each section into subgroups

    :param resume_text: Full plain text of the resume
    :return: A structured dictionary containing parsed data
    """
    # 1) Extract major sections
    sections = extract_sections_from_text(resume_text)

    # 2) Parse each known section
    structured_resume = {}

    # PROFESSIONAL EXPERIENCE
    if "PROFESSIONAL EXPERIENCE" in sections:
        structured_resume["professional_experience"] = parse_professional_experience(
            sections["PROFESSIONAL EXPERIENCE"]
        )

    # EDUCATION
    if "EDUCATION" in sections:
        structured_resume["education"] = parse_education_section(sections["EDUCATION"])

    # SKILLS (or TECHNICAL SKILLS)
    if "TECHNICAL SKILLS" in sections:
        structured_resume["technical_skills"] = parse_skills_section(
            sections["TECHNICAL SKILLS"]
        )

    # PROJECTS
    if "PROJECTS" in sections:
        structured_resume["projects"] = parse_projects_section(sections["PROJECTS"])

    # ADDITIONAL / OTHER
    if "ADDITIONAL INFORMATION" in sections:
        structured_resume["additional_info"] = parse_additional_info(
            sections["ADDITIONAL INFORMATION"]
        )

    # 3) Return the final structured data
    return structured_resume


# =============== Example Usage (Pseudo-Main) ===============
def run_resume_parsing_pipeline(resume_text: str) -> Dict[str, Any]:
    """
    This is the main function that would be called after converting PDF/docx to text.

    :param resume_text: Plain text from resume.
    :return: Dictionary containing structured data for each section/sub-section.
    """
    # 1) Chunk resume into structured subgroups
    structured_data = chunk_resume_into_subgroups(resume_text)

    # 2) (Optional) Post-process or store in database, vector store, etc.
    #    e.g., embed each sub-entry for RAG, store in DB, etc.

    return structured_data


if __name__ == "__main__":
    # If you had the plain text from your resume:
    sample_resume_text = """
    [Your resume text here...]
    """

    # Run the pipeline
    parsed_resume = run_resume_parsing_pipeline(sample_resume_text)

    # Inspect the results
    print(parsed_resume)
