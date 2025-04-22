import os
import requests
from dotenv import load_dotenv
import ast
from utils.credits_tracker import log_usage
from utils.logger_utils import log_anything
import json

# Load the .env file
load_dotenv()


def search_data(
    text: str, model_id: str, category: str = None, operator: str = None, top_k: int = 3
):
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
    log_anything(response.json(), label="search_data (response.json()!!!!)")
    log_usage(
        credits_used=response.json()["usedCredits"],
        transaction_label=f"background seach {category}",
    )
    return response


def process_JSON_api_response(api_response):
    # Just get the full string — no [0]    api_response = api_response.data
    # Parse it safely
    return ast.literal_eval(api_response.data)


def process_standard_agent_api_output(api_response):
    return api_response.data.output


def process_standard_api_output(api_response):
    return api_response.data


import re


def unwrap_triple_backticks(text: str) -> str:
    """
    Checks if 'text' is wrapped in triple backticks (```), optionally with
    a language spec (e.g. ```html), and removes those backticks if present.

    Returns:
        str: The text without surrounding triple backticks.
    """
    # Regex Explanation:
    # ^[\t ]*```         -> start of string + optional whitespace + triple backticks
    # (?:[\w+-]*)?       -> optional language spec (e.g., 'html', 'python', 'js')
    # \r?\n?             -> optional newline(s)
    # (.*?)              -> capture the main content, non-greedy
    # \r?\n?[\t ]*```[\t ]*$ -> closing triple backticks (with optional whitespace) at end of text
    pattern = r"^[\t ]*```(?:[\w+-]*)?\r?\n?(.*?)\r?\n?[\t ]*```[\t ]*$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return text
