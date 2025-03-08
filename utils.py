import os
import csv
from datetime import datetime
import PyPDF2
import docx


def read_txt(file_path):
    """Reads a plain text file, returns string content."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_pdf(file_path):
    """Extracts text from a PDF file using PyPDF2, returns string content."""
    text = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def read_docx_file(file_path):
    """Extracts text from a .docx file using python-docx, returns string content."""
    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)


def extract_text(file_path):
    """
    Determines the file extension and uses the appropriate function
    to extract text. Returns the extracted text or an empty string on unsupported types.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".txt":
        return read_txt(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".docx":
        return read_docx_file(file_path)
    else:
        # You can log this if needed. For now, just return empty to skip.
        return ""


def generate_csv(base_folder, output_csv):
    """
    base_folder structure (example):
        base_folder/
            Resumes/
            CoverLetters/
            Essays/
    Each subfolder is considered 'doc_type'.
    We detect file extension (pdf, docx, txt) and extract text accordingly.
    """
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # CSV header
        writer.writerow(["id", "content", "doc_type", "created_date"])

        # Traverse subfolders
        for doc_type in os.listdir(base_folder):
            doc_type_path = os.path.join(base_folder, doc_type)

            if os.path.isdir(doc_type_path):
                for filename in os.listdir(doc_type_path):
                    file_path = os.path.join(doc_type_path, filename)

                    # Extract text based on file type
                    content = extract_text(file_path)

                    if content.strip():  # If there's any text
                        doc_id = filename.replace(" ", "_")
                        created_date = datetime.now().strftime("%Y-%m-%d")

                        writer.writerow(
                            [
                                doc_id,  # "doc001", or "My_Resume.pdf", etc.
                                content,  # extracted text
                                doc_type,  # "Resumes", "CoverLetters", etc.
                                created_date,
                            ]
                        )
