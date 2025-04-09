import numpy as np
import math
from custom_debugging import debug_display_graph
from nlp.models import (
    nlp,
    model,
    build_similarity_graph,
    compute_average_similarity,
    apply_leiden_clustering,
    compute_dynamic_threshold,
)


def split_into_sentences(full_text: str) -> list[str]:
    """
    Splits a single document's text into individual sentences.

    Args:
        full_text (str): The entire text of one document.

    Returns:
        List[str]: A list of sentences extracted from the document.
    """
    doc = nlp(full_text)
    return [sent.text for sent in doc.sents]


def embed_sentences(sentences: list[str], model=model) -> list[np.ndarray]:
    """
    Embeds each sentence into a dense vector representation using a Transformer model.

    Args:
        sentences (List[str]): A list of sentence strings.

    Returns:
        List[np.ndarray]: A list of embedding vectors, one per sentence.
    """
    return model.encode(sentences, convert_to_numpy=True)


def estimate_token_count(text: str) -> int:
    """
    Estimates the number of tokens in a given text using a transformer tokenizer.

    Args:
        text (str): The text to be tokenized.

    Returns:
        int: An approximate token count.
    """
    return len(model.tokenizer.tokenize(text))


def compute_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Computes the cosine similarity between two embedding vectors using NumPy.

    Args:
        vec_a (np.ndarray): Embedding vector A.
        vec_b (np.ndarray): Embedding vector B.

    Returns:
        float: Cosine similarity in the range [0, 1].
    """
    similarity = np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    return float(similarity)  # Ensure output is a float


def compute_dynamic_resolution(
    n: int,
    T: int,
    S_avg: float,
    base_res: float = 0.6,
    k1: float = 0.03,
    k2: float = 0.2,
) -> float:
    """
    Computes the optimal Leiden resolution dynamically based on text length and similarity.

    Args:
        n (int): Number of sentences.
        T (int): Total token count.
        S_avg (float): Average pairwise similarity between sentences.
        base_res (float): Base resolution (default 0.8).
        k1 (float): Scaling factor for text length.
        k2 (float): Scaling factor for similarity.

    Returns:
        float: The computed resolution value.
    """
    R = base_res + k1 * math.log(n + T + 1) + k2 * (1 - S_avg)
    final = min(max(R, 0.4), 1.5)  # Keep resolution in a reasonable range
    # Debug print
    print(
        "=== compute_dynamic_resolution Debug ===\n"
        f"n         : {n}\n"
        f"T         : {T}\n"
        f"S_avg     : {S_avg:.4f}\n"
        f"base_res  : {base_res}\n"
        f"k1        : {k1}\n"
        f"k2        : {k2}\n"
        f"R (raw)   : {R:.4f}\n"
        f"R (clamped): {final:.4f}\n"
        "========================================"
    )
    return final


def merge_sentences_leiden(
    sentences: list[str],
    embeddings: list[np.ndarray],
    max_token_limit: int,
    similarity_threshold: float = 0.7,
) -> list[str]:
    """
    Merges sentences into chunks using Leiden clustering with dynamic resolution.

    Args:
        sentences (List[str]): List of sentences.
        embeddings (List[np.ndarray]): Corresponding sentence embeddings.
        max_token_limit (int): Maximum token limit per chunk.

    Returns:
        List[str]: List of merged text chunks.
    """
    # 1. Compute dynamic threshold
    threshold = compute_dynamic_threshold(
        embeddings, percentile=75, lower_bound=0.3, upper_bound=0.7
    )
    n = len(sentences)
    T = sum(estimate_token_count(sent) for sent in sentences)
    S_avg = compute_average_similarity(embeddings)

    # Compute optimal resolution
    resolution = compute_dynamic_resolution(n, T, S_avg)
    # for debugging
    # print(f"resolution: {resolution}")

    # Build similarity graph
    graph = build_similarity_graph(sentences, embeddings, threshold)
    # for debugging
    # debug_display_graph(graph, embeddings, sentences, threshold=threshold)

    # Run Leiden clustering
    clusters = apply_leiden_clustering(graph, resolution)

    # Merge sentences within each cluster
    merged_chunks = []
    for cluster in clusters:
        cluster_sentences = [sentences[i] for i in sorted(cluster)]  # Preserve order
        # merged_text = " ".join(cluster_sentences)
        merged_text = "\n---\n".join(cluster_sentences)  # Separate with a clear marker
        # merged_chunks.append(f"[MERGED] {merged_text}")

        # Ensure the chunk does not exceed max_token_limit
        if estimate_token_count(merged_text) > max_token_limit:
            # Split into smaller chunks if needed
            split_chunks = []
            current_chunk = ""
            for sent in cluster_sentences:
                if estimate_token_count(current_chunk + " " + sent) > max_token_limit:
                    split_chunks.append(current_chunk.strip())
                    current_chunk = sent
                else:
                    current_chunk += " " + sent
            if current_chunk:
                split_chunks.append(current_chunk.strip())
            # merged_chunks.extend([f"[MERGED] {chunk}" for chunk in split_chunks]) # for debugging
            merged_chunks.extend([chunk for chunk in split_chunks])
        else:
            # merged_chunks.append(f"[MERGED] {merged_text}") #for debugging
            merged_chunks.append(merged_text)

    # Include sentences that were not clustered
    all_indices = set(range(len(sentences)))
    clustered_indices = {i for cluster in clusters for i in cluster}
    unclustered_indices = all_indices - clustered_indices

    for idx in unclustered_indices:
        merged_chunks.append(
            # f"[SINGLE] {sentences[idx]}" #tagged for debugging
            sentences[idx]
        )
    return merged_chunks
