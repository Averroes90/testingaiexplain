# GPT 4 (32k) on Azure
from aixplain.factories import ModelFactory

scrape_summary_model = ModelFactory.get("655b99506eb5634de57292a1")

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
            {"role": "user", "content": f"{result}"},
        ],
        "max_tokens": 2000,
    }
)

print(api_response)
