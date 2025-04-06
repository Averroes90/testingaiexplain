def parse_resume_sections(parsed_lines):
    """
    Orchestrates the parsing of resume data into the specified categories.

    :param parsed_lines: A list of line objects, each having structure similar to:
        {
            'line': str,
            'is_visually_separated': bool,
            'contains_bullet': bool,
            'contains_contact_info': bool,
            'ends_with_conjunction': bool,
            'starts_with_conjunction': bool,
            'zero_shot_classification': {'label': str, 'score': float},
            'named_entity_recognition': list of entities,
            'is_section_header': bool or None
        }
    :return: A dictionary with the following keys:
        {
            "name": ...,
            "contact_info": ...,
            "technical_skills": ...,
            "professional_experience": ...,
            "education": ...,
            "technical_projects": ...,
            "additional_information": ...,
            "other": ...
        }
    """

    # 1. Name
    name, parsed_lines = parse_name(parsed_lines)

    # 2. Contact Info
    contact_info, parsed_lines = parse_contact_info(parsed_lines)

    # 3. Technical Skills
    technical_skills, parsed_lines = parse_technical_skills(parsed_lines)

    # 4. Professional Experience
    professional_experience, parsed_lines = parse_professional_experience(parsed_lines)

    # 5. Education
    education, parsed_lines = parse_education(parsed_lines)

    # 6. Technical Projects
    technical_projects, parsed_lines = parse_technical_projects(parsed_lines)

    # 7. Additional Information
    additional_information, parsed_lines = parse_additional_information(parsed_lines)

    # 8. Everything Else / Fallback
    other = parse_other_sections(parsed_lines)

    # Assemble final dictionary
    resume_data = {
        "name": name,
        "contact_info": contact_info,
        "technical_skills": technical_skills,
        "professional_experience": professional_experience,
        "education": education,
        "technical_projects": technical_projects,
        "additional_information": additional_information,
        "other": other,
    }

    return resume_data


def parse_name(parsed_lines):
    """
    Extracts the FIRST occurrence of a line whose named_entity_recognition
    contains only PER (person) entities, and no other entity type.
    Once found, that line is removed from parsed_lines.

    :param parsed_lines: List of line dictionaries.
    :return: (name, updated_parsed_lines)
    """
    name = None

    for i, line in enumerate(parsed_lines):
        ner_entries = line.get("named_entity_recognition", [])
        if ner_entries:
            # Check if ALL entities in this line are labeled 'PER'
            if all(ent.get("label") == "PER" for ent in ner_entries):
                name = line["line"]
                # Remove from the list so we don't parse it twice
                del parsed_lines[i]
                break

    return name, parsed_lines


def parse_contact_info(parsed_lines):
    """
    Collects all lines whose zero-shot classification label is CONTACT INFO.
    Removes each matching line from the list.

    :param parsed_lines: List of line dictionaries.
    :return: (list_of_contact_info_lines, updated_parsed_lines)
    """
    contact_info_lines = []

    i = 0
    while i < len(parsed_lines):
        line = parsed_lines[i]
        zsc_label = line.get("zero_shot_classification", {}).get("label", "").upper()
        if zsc_label == "CONTACT INFO":
            contact_info_lines.append(line["line"])
            del parsed_lines[i]
        else:
            i += 1
    contact_string = "\n".join(contact_info_lines)
    return contact_string, parsed_lines


def get_section_by_header(header_label, parsed_lines):
    """
    A helper that finds a given header_label in parsed_lines (via is_section_header),
    returns all lines (excluding the header line) from that header until the next different
    header is encountered (or end of list) as a single string with newlines separating lines.
    Those lines are removed from parsed_lines.

    :param header_label: String, e.g. "TECHNICAL SKILLS", "PROFESSIONAL EXPERIENCE"
    :param parsed_lines: The list of parsed line dictionaries
    :return: (section_string, updated_parsed_lines)
    """
    section_lines = []
    i = 0

    while i < len(parsed_lines):
        line = parsed_lines[i]
        if line.get("is_section_header") == header_label:
            # Found the header; remove it and skip adding it to the output.
            del parsed_lines[i]

            # Now capture subsequent lines until we reach a new/different section header.
            while i < len(parsed_lines):
                next_line = parsed_lines[i]
                next_header = next_line.get("is_section_header")
                if next_header is not None and next_header != header_label:
                    break

                section_lines.append(next_line["line"])
                del parsed_lines[i]

            # Only process the first matching section header.
            break
        else:
            i += 1

    section_string = "\n".join(section_lines)
    return section_string, parsed_lines


def parse_technical_skills(parsed_lines):
    """
    Finds the "TECHNICAL SKILLS" section using our helper function
    and returns its lines, removing them from parsed_lines.
    """
    tech_skills_section, parsed_lines = get_section_by_header(
        "TECHNICAL SKILLS", parsed_lines
    )
    return tech_skills_section, parsed_lines


def parse_professional_experience(parsed_lines):
    """
    Finds the "PROFESSIONAL EXPERIENCE" section, then calls parse_by_company
    to structure the data by employer, roles, etc.
    """
    experience_section, parsed_lines = get_section_by_header(
        "PROFESSIONAL EXPERIENCE", parsed_lines
    )

    # parse_by_company will handle the deeper structure of the lines
    # returned from the "PROFESSIONAL EXPERIENCE" section.
    structured_experience = parse_by_company(experience_section)

    return experience_section, parsed_lines
    return structured_experience, parsed_lines


def parse_by_company(experience_lines):
    """
    Placeholder for parsing out the experience lines by company/employer.
    Potential approach:
    - Identify each employer boundary.
    - For each employer, parse the roles, date range, location, etc.

    Returns a list or dict structure containing the segmented professional experience.
    """
    # Example: we might return something like:
    # [
    #   {
    #     "employer": "Some Company",
    #     "roles": [
    #       {
    #         "title": "Software Engineer",
    #         "dates": "Jan 2020 - Present",
    #         "location": "San Francisco, CA",
    #         "responsibilities": ["...", "..."]
    #       },
    #       ...
    #     ]
    #   },
    #   ...
    # ]
    # But for now, just a placeholder.

    # This is where you'd call parse_by_role, extract_date, etc.

    return []  # Placeholder


def parse_by_role(role_lines):
    """
    A placeholder function that would parse out a single role
    (title, date range, responsibilities, etc.) from the lines provided.
    """
    # Example return structure:
    # {
    #   "title": "...",
    #   "dates": "...",
    #   "location": "...",
    #   "responsibilities": [...]
    # }
    return {}


def extract_date(line):
    """
    A placeholder function for extracting date information from a line (e.g., "Jan 2020 - Present").
    """
    return None


def extract_location(line):
    """
    A placeholder function for extracting location data (e.g., "San Francisco, CA") from a line.
    """
    return None


def parse_education(parsed_lines):
    """
    Extracts education details:
      - School
      - Degree
      - Additional info under degree
      - Graduation date
    (Implementation TBD)
    """
    education_section, parsed_lines = get_section_by_header("EDUCATION", parsed_lines)
    return education_section, parsed_lines


def parse_technical_projects(parsed_lines):
    """
    Identifies and parses technical project descriptions,
    including details relevant to each project.
    (Implementation TBD)
    """
    projects_section, parsed_lines = get_section_by_header(
        "SELECTED TECHNICAL PROJECTS", parsed_lines
    )
    return projects_section, parsed_lines


def parse_additional_information(parsed_lines):
    """
    Extracts additional information (certifications, awards,
    volunteering, etc.).
    (Implementation TBD)
    """
    add_info_section, parsed_lines = get_section_by_header(
        "ADDITIONAL INFORMATION & PROFESSIONAL DEVELOPMENT", parsed_lines
    )
    return add_info_section, parsed_lines


def parse_other_sections(parsed_lines):
    """
    Fallback parser that returns the remaining lines as plain text,
    stripping away any associated metadata.

    :param parsed_lines: List of line dictionaries that have not been parsed by other functions.
    :return: A list of plain text strings representing the remaining lines.
    """
    other_string = "\n".join([line["line"] for line in parsed_lines])
    return other_string
