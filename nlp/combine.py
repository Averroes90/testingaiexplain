from chunking import chunk_free_form
from chunking import chunk_sections
from chunking.chunk_merge import merge_line_chunks
from chunking.extract_sections import parse_resume_sections
import csv
import os


def handle_free_form(content, similarity_threshold=0.6, max_tokens=300):
    sents = chunk_free_form.split_into_sentences(content)
    embeddings = chunk_free_form.embed_sentences(sents)
    similarity_threshold = similarity_threshold
    max_tokens = max_tokens
    merged_sents = chunk_free_form.merge_sentences_leiden(
        sents,
        embeddings,
        max_token_limit=max_tokens,
        similarity_threshold=similarity_threshold,
    )
    return merged_sents


def handle_resume(content):
    lines = chunk_sections.parse_into_lines(content)
    table1 = chunk_sections.generate_line_features(lines)
    merged_lines = merge_line_chunks(table1)
    table2 = chunk_sections.generate_line_features(merged_lines)
    parsed_resume = parse_resume_sections(table2)
    return parsed_resume


def process_dataframe(data_df):
    parsed_resumes = {}
    parsed_essays = {}
    for index, row in data_df.iterrows():
        content = row["content"]
        doc_id = row["id"]
        if row["doc_type"] == "Resumes":
            # Assuming handle_resume returns a dictionary with key/value pairs
            parsed_resume = handle_resume(content=content)
            parsed_resumes[doc_id] = parsed_resume
        else:
            # Assuming handle_free_form returns a list of sentences/contents
            sents = handle_free_form(content=content)
            parsed_essays[doc_id] = sents
    return parsed_resumes, parsed_essays


def create_resumes_csv(parsed_resumes, directory):
    # Ensure the target directory exists
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, "resumes.csv")

    # Build a list of rows. For each resume, add the id as a new key.
    rows = []
    all_keys = set()
    for resume_id, resume_data in parsed_resumes.items():
        # Create a new dictionary that includes the resume id as "id"
        row_dict = {"id": resume_id}
        row_dict.update(resume_data)
        rows.append(row_dict)
        all_keys.update(row_dict.keys())

    # Ensure "id" is the first column
    all_keys = list(all_keys)
    if "id" in all_keys:
        all_keys.remove("id")
        all_keys = ["id"] + sorted(all_keys)
    else:
        all_keys = sorted(all_keys)

    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def create_essays_csv(parsed_essays, directory):
    # Ensure the target directory exists
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, "essays.csv")

    # Write the data to the CSV file with header "id" and "content"
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "content"])
        for essay_id, contents in parsed_essays.items():
            for content in contents:
                writer.writerow([essay_id, content])


def create_combined_csv(parsed_resumes, parsed_essays, directory):
    # Ensure the target directory exists
    os.makedirs(directory, exist_ok=True)
    csv_file_path = os.path.join(directory, "combined.csv")

    # Open the file and write the header and rows
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["id", "category", "content"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process resumes: each key/value pair becomes a separate row.
        for doc_id, resume_data in parsed_resumes.items():
            for key, value in resume_data.items():
                category = f"resume-{key}"
                writer.writerow({"id": doc_id, "category": category, "content": value})

        # Process essays: each item in the list becomes a separate row with category "free-form".
        for doc_id, essay_contents in parsed_essays.items():
            for content in essay_contents:
                writer.writerow(
                    {"id": doc_id, "category": "free-form", "content": content}
                )
