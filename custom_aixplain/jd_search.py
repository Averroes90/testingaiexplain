from custom_aixplain.utils import search_data
from utils.config_loader import load_config
import json
from utils.credits_tracker import log_usage


def search_background_first_pass(job_info: dict) -> dict:
    config = load_config()
    resume_model_id = config["resume_model_id"]
    essay_model_id = config["essay_model_id"]

    job_description = job_info["summary"]
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
        category="education",
        operator="==",
        model_id=resume_model_id,
        top_k=1,
    )

    education = result.json()["data"]

    # Other Resume Entries
    result = search_data(
        f"search the data base containing my resume info for entries that most align with this job description:{job_description} ",
        category=["professional_experience", "education"],
        operator="not in",
        model_id=resume_model_id,
    )

    other_resume = [item["data"] for item in result.json()["details"]]

    # Essays
    result = search_data(
        f"search the data base for entries that most align with this job description:{job_description} ",
        category="free-form",
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


def get_relevant_background_info(user_query: str) -> dict:
    config = load_config()
    resume_model_id = config["resume_model_id"]
    essay_model_id = config["essay_model_id"]

    # structured
    result = search_data(
        f"search the data base containing my resume info for entries that most align with this: {user_query} ",
        model_id=resume_model_id,
        top_k=2,
    )
    structured = [item["data"] for item in result.json()["details"]]

    result = search_data(
        f"search the data base for entries that most align with this: {user_query} ",
        "free-form",
        operator="==",
        model_id=essay_model_id,
        top_k=2,
    )
    free_form = [item["data"] for item in result.json()["details"]]
    return {
        "structured": structured,
        "free_form": free_form,
    }
