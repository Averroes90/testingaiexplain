from custom_aixplain.models import scrape_summary_model
from custom_aixplain.my_custom_tools import scrape_and_clean_link


def scrape_job_info(url: str):

    raw_content = scrape_and_clean_link(url)

    api_response = scrape_summary_model.run(
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

    return api_response


from custom_aixplain.agents import writer_agent, formatter_agent
from custom_aixplain.pipelines import scrape_job_info
from custom_aixplain.utils import process_JSON_api_response, process_standard_api_output
from pipelines.jd_search import (
    search_background_first_pass,
    get_relevant_background_info,
)
import json


def first_pass_pipeline(variables: dict):

    return_dict = {}
    raw_scrape = scrape_job_info(variables["url"])
    job_info = process_JSON_api_response(raw_scrape)
    return_dict["job_info"] = job_info
    background_info = search_background_first_pass(job_info)
    return_dict["background_info"] = background_info
    for i, doc_type in enumerate(variables["doc_type"]):
        style = variables["style"][i]
        page_count = variables["page_count"][i]
        raw_text = writer_agent.run(
            query=f"Generate a {doc_type} referencing '{job_info}' and {background_info} with page count {page_count}. Return plain text or minimal JSON.",
            max_tokens=2000,
        )
        print(f"resume raw text api response {raw_text}")
        raw_text = process_standard_api_output(raw_text)
        print(f"resume raw text processed {raw_text}")
        formatted_text = formatter_agent.run(
            query=f"Format this new {doc_type} text in {raw_text} using {style} style, aiming for {page_count} A4 pages. Return valid HTML only, with professional headings and bullet points. contact info and address on one line",
            max_tokens=2000,
        )
        formatted_text = process_standard_api_output(formatted_text)
        return_dict[doc_type] = formatted_text
    return return_dict
