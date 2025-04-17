# File: resume_parser_project/nlp/zsc.py

from transformers import pipeline
import utils.utils as utils
from collections import defaultdict


def load_zsc_model(model_name: str = "facebook/bart-large-mnli"):
    """
    Loads a zero-shot classification model from Hugging Face,
    returning a pipeline object that can be reused across the app.

    :param model_name: The Hugging Face model name/path to load.
                       Defaults to 'facebook/bart-large-mnli'.
    :return: A transformers pipeline for zero-shot classification.
    """
    zsc_pipeline = pipeline(
        "zero-shot-classification",  # We want the zero-shot pipeline
        model=model_name,  # The pre-trained model to load
        # hypothesis_template="This text belongs to the category of {}.",
    )
    return zsc_pipeline


def classify_line_zsc(line: str, zsc_pipeline=None) -> list[dict[str, float]]:
    """
    Runs zero-shot classification on a line of text using canonical labels and their synonyms.
    Aggregates scores under each canonical label.

    :param line: The text line to classify.
    :param zsc_pipeline: Hugging Face zero-shot classification pipeline.
    :return: List of dicts with canonical label and aggregated score, sorted descending.
    """
    if zsc_pipeline is None:
        zsc_pipeline = load_zsc_model()
    # 1. Load flat label map
    headings_json_path = "config/labels.json"
    flat_map = utils.load_flat_labels(
        headings_json_path
    )  # Assuming utils.load_flat_labels is imported as load_flat_labels

    # 2. Prepare candidate labels (synonyms + canonical)
    candidate_labels = list(flat_map.keys())
    # 3. Run zero-shot classification
    classification = zsc_pipeline(line, candidate_labels=candidate_labels)

    # 4. Aggregate scores by canonical label
    canonical_scores = defaultdict(float)

    for label, score in zip(classification["labels"], classification["scores"]):
        canonical_label = flat_map[label.lower()]["canonical_label"]
        canonical_scores[canonical_label] += score

    # 5. Return sorted list of canonical labels by aggregated score
    sorted_results = sorted(
        [
            {"label": label, "score": round(score, 4)}
            for label, score in canonical_scores.items()
        ],
        key=lambda x: x["score"],
        reverse=True,
    )

    return sorted_results
