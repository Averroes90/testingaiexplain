import os
import requests
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


def search_data(text: str, category: str, operator: str, model_id: str, top_k: int = 3):
    """
    Search the index based on the given category filter.
    """
    api_key = os.getenv("AIXPLAIN_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Make sure AIXPLAIN_API_KEY is set in the .env file."
        )

    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    payload = {
        "action": "search",
        "data": text,
        "dataType": "text",
        "payload": {
            "top_k": top_k,
        },
    }
    if category == "None":
        category = None
    else:

        payload["payload"]["filters"] = {
            "field": "meta.attributes.category",
            "operator": operator,
            "value": category,
        }

    response = requests.post(
        f"https://models.aixplain.com/api/v2/execute/{model_id}",
        headers=headers,
        json=payload,
    )
    return response
