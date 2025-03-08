import numpy as np


def split_into_sentences(full_text: str) -> list[str]:
    """
    Splits a single document's text into individual sentences.

    Args:
        full_text (str): The entire text of one document.

    Returns:
        List[str]: A list of sentences extracted from the document.
    """
    return []


def embed_sentences(sentences: list[str]) -> list[np.ndarray]:
    """
    Embeds each sentence into a dense vector representation.

    Args:
        sentences (List[str]): A list of sentence strings.

    Returns:
        List[np.ndarray]: A list of embedding vectors, one per sentence.
    """
    return []
