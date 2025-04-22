from custom_aixplain.models import llm_model_api
from custom_aixplain.my_custom_tools import scrape_and_clean_link
from utils.credits_tracker import log_usage
from utils.logger_utils import log_anything


def scrape_job_info(url: str):

    raw_content = scrape_and_clean_link(url)

    api_response = llm_model_api.run(
        {
            "text": [
                {
                    "role": "system",
                    "content": (
                        "You parse raw job listings. Remove ads and irrelevant text, "
                        "merge or briefly summarize generic/repetitive tasks, and keep all specific "
                        "skills, tech, and named entities. Return valid JSON ONLY with keys: company, title, summary."
                    ),
                },
                {"role": "user", "content": f"{raw_content}"},
            ],
            "max_tokens": 2000,
        }
    )
    log_anything(api_response, label="scrape job info")
    log_usage(
        credits_used=api_response.used_credits,
        prompt_tokens_used=api_response.usage["prompt_tokens"],
        completion_tokens_used=api_response.usage["completion_tokens"],
        transaction_label="scrape job info clean-up",
    )
    return api_response


def document_write(query):

    api_response = llm_model_api.run(
        {
            "text": [
                {
                    "role": "system",
                    "content": (
                        "You can:\n"
                        "1) CREATE a new document (resume or cover letter), given:\n"
                        '   - doc_type ("resume" or "cover_letter")\n'
                        "   - job_info\n"
                        "   - background_info\n"
                        "   - page_count (number of A4 pages)\n"
                        "2) UPDATE an existing document, given:\n"
                        "   - doc_type\n"
                        "   - current_text\n"
                        "   - new_background_snippet (optional)\n"
                        "   - user_request\n"
                        "   - page_count\n"
                        "\n"
                        "Respect page_count when deciding how much detail to include. "
                        "If current_text is provided, preserve it but integrate new info or changes. "
                        "Return plain text or minimal JSON only—no extra commentary.\n"
                        "\n"
                        "For 'resume', keep it concise and relevant.\n"
                        "For 'cover_letter', address the company/role and highlight key qualifications.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": f"{query}",  # or f"{query}" if that's your actual data variable
                },
            ],
            "max_tokens": 4000,
        }
    )
    log_anything(api_response, label="document write")
    log_usage(
        credits_used=api_response.used_credits,
        prompt_tokens_used=api_response.usage["prompt_tokens"],
        completion_tokens_used=api_response.usage["completion_tokens"],
        transaction_label="document write",
    )
    return api_response


def document_format(query: str):

    api_response = llm_model_api.run(
        {
            "text": [
                {
                    "role": "system",
                    "content": (
                        "You convert or update resume/cover-letter text into concise, clean HTML. "
                        "You may receive:\n"
                        " - 'raw_text' (new or updated content),\n"
                        " - 'existing_formatted_html' (previous styling),\n"
                        " - 'style' ('professional' or 'modern'),\n"
                        " - 'page_count' (A4 pages),\n"
                        " - 'doc_type' ('resume' or 'cover_letter'),\n"
                        " - 'user_request' (styling instructions).\n"
                        "\n"
                        "When both 'existing_formatted_html' and 'raw_text' are provided, merge or adjust them. "
                        "Keep the document within 'page_count' if possible, without removing critical details.\n"
                        "\n"
                        "Formatting Guidelines:\n"
                        "1. Return only the final HTML (no extra text).\n"
                        "2. Use a standard, easy-to-read font. Keep headings consistent.\n"
                        "3. Align bullets and non-bulleted text to the same left margin. Avoid multiple nested bullet levels.\n"
                        "4. If 'doc_type' = 'resume', format job titles, company names, and dates consistently; use bullet points for accomplishments.\n"
                        "5. If 'doc_type' = 'cover_letter', maintain a typical letter structure (date, greeting, body, closing).\n"
                        "6. Apply minimal color, unless 'style' is 'modern' (then subtle accents are acceptable).\n"
                        "\n"
                        "Do not add or change the original text beyond minor formatting adjustments. "
                        "Output only the well-formatted HTML.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": f"{query}",  # or f"{query}", whichever holds the actual text
                },
            ],
            "max_tokens": 10000,
        }
    )
    log_anything(api_response, label="document format")
    log_usage(
        credits_used=api_response.used_credits,
        prompt_tokens_used=api_response.usage["prompt_tokens"],
        completion_tokens_used=api_response.usage["completion_tokens"],
        transaction_label="document format",
    )
    return api_response


# from custom_aixplain.agents import writer_agent, formatter_agent
# from custom_aixplain.pipelines import scrape_job_info
# from custom_aixplain.utils import process_JSON_api_response, process_standard_api_output
# from pipelines.jd_search import (
#     search_background_first_pass,
#     get_relevant_background_info,
# )
# import json


# def first_pass_pipeline(variables: dict):

#     return_dict = {}
#     raw_scrape = scrape_job_info(variables["url"])
#     job_info = process_JSON_api_response(raw_scrape)
#     return_dict["job_info"] = job_info
#     background_info = search_background_first_pass(job_info)
#     return_dict["background_info"] = background_info
#     for i, doc_type in enumerate(variables["doc_type"]):
#         style = variables["style"][i]
#         page_count = variables["page_count"][i]
#         raw_text = writer_agent.run(
#             query=f"Generate a custom {doc_type} referencing '{job_info}' and {background_info} with page count {page_count}. Return plain text or minimal JSON.",
#             max_tokens=4000,
#         )
#         print(f"resume raw text api response {raw_text}")
#         raw_text = process_standard_agent_api_output(raw_text)
#         print(f"resume raw text processed {raw_text}")
#         formatted_text = formatter_agent.run(
#             query=f"Format this new {doc_type} text in {raw_text} using {style} style, aiming for {page_count} A4 pages. Return valid HTML only, with professional headings and bullet points. contact info and address on one line",
#             max_tokens=4000,
#         )
#         formatted_text = process_standard_agent_api_output(formatted_text)
#         return_dict[doc_type] = formatted_text
#     return return_dict

from custom_aixplain.pipelines import scrape_job_info, document_format, document_write
from custom_aixplain.utils import process_JSON_api_response, process_standard_api_output
from custom_aixplain.jd_search import (
    search_background_first_pass,
)
import json
from custom_aixplain.utils import unwrap_triple_backticks
from utils.logger_utils import log_anything


def first_pass_pipeline(variables: dict):

    return_dict = {}
    raw_scrape = scrape_job_info(variables["url"])
    job_info = process_JSON_api_response(raw_scrape)
    log_anything(job_info, label="job_info")
    return_dict["job_info"] = job_info
    background_info = search_background_first_pass(job_info)
    log_anything(background_info, label="background_info")
    return_dict["background_info"] = background_info
    for i, doc_type in enumerate(variables["doc_type"]):
        style = variables["style"][i]
        page_count = variables["page_count"][i]
        raw_text = document_write(
            query=f"Generate a {doc_type} referencing '{job_info}' and {background_info} with content enough to fill {page_count} A4 pages. Return plain text or minimal JSON."
        )
        raw_text = process_standard_api_output(raw_text)
        log_anything(raw_text, label="processed raw text")
        formatted_text = document_format(
            query=f"Format this new {doc_type} text in {raw_text} using {style} style, aiming for {page_count} A4 pages. Return valid HTML only, with professional headings and bullet points where appropriate. contact info and address on one line."
        )
        formatted_text = process_standard_api_output(formatted_text)
        log_anything(formatted_text, label="processed formatted text")
        formatted_text = unwrap_triple_backticks(formatted_text)
        log_anything(
            formatted_text, label="formatted text after removing triple backticks"
        )
        return_dict[doc_type] = formatted_text
    log_anything(return_dict, label="return dict")
    return return_dict
