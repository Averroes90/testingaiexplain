# File: resume_parser_project/nlp/zsc.py

from transformers import pipeline
import utils
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


# File: resume_parser_project/nlp/zsc.py


# def classify_chunks_zsc(chunks: list[str], zsc_pipeline) -> list[dict]:
#     """
#     Runs zero-shot classification on a list of text chunks,
#     using all keys from 'flat_map' (the flattened synonyms) as candidate labels.

#     The 'flat_map' is the dictionary returned by load_flat_labels, something like:
#     {
#       "professional experience": {
#         "label_type": "SECTION_HEADING",
#         "canonical_label": "PROFESSIONAL EXPERIENCE",
#         "belongs_to": None
#       },
#       "work experience": {
#         "label_type": "SECTION_HEADING",
#         "canonical_label": "PROFESSIONAL EXPERIENCE",
#         "belongs_to": None
#       },
#       "company line": {
#         "label_type": "SUB_LABEL",
#         "canonical_label": "Company Line",
#         "belongs_to": "PROFESSIONAL EXPERIENCE"
#       },
#       ...
#     }

#     For each chunk:
#       1. We pass it to 'zsc_pipeline' with all synonyms as candidate labels.
#       2. We take the highest-score label from the pipeline's output.
#       3. We look that label up in 'flat_map' to retrieve the canonical label
#          and label type (SECTION_HEADING vs SUB_LABEL).

#     Returns a list of dicts, e.g.:
#     [
#       {
#         "chunk": "...",
#         "predicted_synonym": "work experience",
#         "score": 0.93,
#         "canonical_label": "PROFESSIONAL EXPERIENCE",
#         "label_type": "SECTION_HEADING",
#         "belongs_to": None
#       },
#       ...
#     ]
#     """
#     # flat_map = load_secction_headings()
#     headings_json_path = "config/labels.json"
#     flat_map = utils.load_flat_labels(headings_json_path)
#     # 1) Gather all synonyms from flat_map for zero-shot candidate labels
#     candidate_labels = list(flat_map.keys())

#     results = []

#     for chunk in chunks:
#         # 2) Run zero-shot classification with the chunk
#         classification = zsc_pipeline(chunk, candidate_labels=candidate_labels)

#         # classification["labels"] is a list in descending confidence order
#         top_label: str = classification["labels"][0]  # e.g. "work experience"
#         top_score: float = classification["scores"][0]

#         # 3) Lookup the label in our flat_map to find metadata
#         #    We lowercase 'top_label' because flat_map keys are stored in lowercased form
#         top_label_lower = top_label.lower()

#         metadata = flat_map.get(top_label_lower, None)
#         print("\n-----CHUNK -----")
#         print(chunk)
#         print("\n-----top_label_lower -----")
#         print(top_label_lower)
#         print("\n-----metadata -----")
#         print(metadata)
#         print("\n-----classification -----")
#         print(classification)
#         # If not found (edge case), we skip or store partial info
#         if metadata is None:
#             results.append(
#                 {
#                     "chunk": chunk,
#                     "predicted_synonym": top_label,
#                     "score": top_score,
#                     "canonical_label": None,
#                     "label_type": None,
#                     "belongs_to": None,
#                 }
#             )
#             continue

#         # 4) Build a result dict
#         results.append(
#             {
#                 "chunk": chunk,
#                 "predicted_synonym": top_label,  # e.g. "work experience"
#                 "score": top_score,
#                 "canonical_label": metadata[
#                     "canonical_label"
#                 ],  # e.g. "PROFESSIONAL EXPERIENCE"
#                 "label_type": metadata["label_type"],  # e.g. "SECTION_HEADING"
#                 "belongs_to": metadata[
#                     "belongs_to"
#                 ],  # e.g. None or "PROFESSIONAL EXPERIENCE"
#             }
#         )

#     return results


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
