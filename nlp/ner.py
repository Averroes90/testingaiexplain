# File: resume_parser_project/nlp/ner.py

from transformers import pipeline


def load_ner_model(model_name: str = "xlm-roberta-large-finetuned-conll03-english"):
    """
    Loads a Named Entity Recognition (NER) model using the Hugging Face transformers library.
    Defaults to the 'dslim/bert-base-NER' model, which is well-known for NER tasks.

    :param model_name: The model name or path. You can replace this with any other
                       NER-focused model on Hugging Face.
    :return: A transformers pipeline for token classification (NER).
    """
    # aggregation_strategy="simple" merges wordpieces into single entities
    ner_pipeline = pipeline(
        "token-classification",
        model=model_name,
        aggregation_strategy="simple",
    )
    return ner_pipeline


def run_ner_on_chunks(chunks: list[str], ner_pipeline) -> list[dict]:
    """
    Applies the NER pipeline to each text chunk and returns the recognized entities.

    :param chunks: A list of text chunks (strings) to process.
    :param ner_pipeline: The NER pipeline (returned by load_ner_model).
    :return: A list of dicts, each with:
             {
               "chunk": str,
               "entities": [
                 {
                   "entity_group": "ORG",
                   "score": 0.99,
                   "word": "Google LLC",
                   "start": 0,
                   "end": 10
                 },
                 ...
               ]
             }
    """
    results = []

    for chunk in chunks:
        # The pipeline returns a list of entity dicts for each chunk
        entities = ner_pipeline(chunk)
        # e.g. [ {entity_group: "ORG", "score": 0.99, "word": "Google", ...}, ... ]

        results.append({"chunk": chunk, "entities": entities})

    return results


def extract_ner(text: str, ner_pipeline=None) -> list[dict]:
    """
    Extracts named entities from a line using the given NER pipeline.

    :param text: The input text line.
    :param ner_pipeline: A Hugging Face token-classification pipeline (NER).
    :return: A list of dicts representing named entities with label, text, and score.
    """
    if ner_pipeline is None:
        ner_pipeline = load_ner_model()
    try:
        entities = ner_pipeline(text)
        results = [
            {
                "text": ent["word"],
                "label": ent["entity_group"],
                "score": round(ent["score"], 4),
            }
            for ent in entities
        ]
        return results
    except Exception as e:
        # In case of pipeline or model error, return empty list
        return []
