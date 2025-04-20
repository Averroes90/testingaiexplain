from custom_aixplain.models import scrape_summary_model
from custom_aixplain.my_custom_tools import scrape_and_clean_link
from custom_aixplain.utils import process_scrape_response


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
