from custom_aixplain.utils import search_data
from utils.config_loader import load_config
import json


def search_background(job_description: str) -> dict:
    config = load_config()
    resume_model_id = config["resume_model_id"]
    essay_model_id = config["essay_model_id"]

    # Professional Experience
    result = search_data(
        f"search the data base containing my resume info for entries that most align with this job description:{job_description} ",
        category="professional_experience",
        operator="==",
        model_id=resume_model_id,
        top_k=1,
    )
    professional_experience = result.json()["data"]

    # Education
    result = search_data(
        f"search the data base containing my resume info for entries that most align with this job description:{job_description} ",
        "education",
        operator="==",
        model_id=resume_model_id,
        top_k=1,
    )
    education = result.json()["data"]

    # Other Resume Entries
    result = search_data(
        f"search the data base containing my resume info for entries that most align with this job description:{job_description} ",
        ["professional_experience", "education"],
        operator="not in",
        model_id=resume_model_id,
    )
    other_resume = [item["data"] for item in result.json()["details"]]

    # Essays
    result = search_data(
        f"search the data base for entries that most align with this job description:{job_description} ",
        "free-form",
        operator="==",
        model_id=essay_model_id,
        top_k=5,
    )
    essays = [item["data"] for item in result.json()["details"]]

    return {
        "professional_experience": professional_experience,
        "education": education,
        "other_resume": other_resume,
        "essays": essays,
    }
