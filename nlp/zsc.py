# File: resume_parser_project/nlp/zsc.py

from transformers import pipeline


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
    )
    return zsc_pipeline
