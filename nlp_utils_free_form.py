import numpy as np
import spacy
from sentence_transformers import SentenceTransformer, util
import networkx as nx
import leidenalg
import igraph as ig
import math
from custom_debugging import debug_display_graph

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Load a high-quality sentence embedding model
# model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and accurate

model = SentenceTransformer("all-mpnet-base-v2")  # Best accuracy
# or
# model = SentenceTransformer("all-distilroberta-v1")  # Speed & accuracy balance
# # or
# model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")  # Thematic clustering


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


def embed_sentences(sentences: list[str]) -> list[np.ndarray]:
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


def compute_average_similarity(embeddings: list[np.ndarray]) -> float:
    """
    Computes the average cosine similarity between all sentence embeddings.

    Args:
        embeddings (List[np.ndarray]): List of sentence embeddings.

    Returns:
        float: The average similarity score (0 to 1).
    """
    if len(embeddings) < 2:
        return 0.0  # Default for single sentence inputs

    similarity_matrix = util.cos_sim(
        embeddings, embeddings
    )  # Computes pairwise cosine similarity
    n = len(embeddings)

    # Compute average similarity (excluding diagonal self-similarity)
    total_sim = (similarity_matrix.sum() - n) / (n * (n - 1)) if n > 1 else 0.0
    print(f"total similarity: {float(total_sim)}")
    return float(total_sim)


def build_similarity_graph(
    sentences: list[str], embeddings: list[np.ndarray], threshold: float = 0.7
) -> nx.Graph:
    """
    Builds a similarity graph where edges represent sentence similarity.

    Args:
        sentences (List[str]): List of sentences.
        embeddings (List[np.ndarray]): Corresponding sentence embeddings.
        threshold (float): Minimum similarity to create an edge.

    Returns:
        nx.Graph: A NetworkX graph with sentence indices as nodes.
    """
    G = nx.Graph()
    for i in range(len(sentences)):
        G.add_node(i, text=sentences[i])  # Add sentence index as a node

    # Compute pairwise cosine similarity
    similarity_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()

    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = similarity_matrix[i][j]
            if similarity >= threshold:
                G.add_edge(i, j, weight=similarity)

    return G


def apply_leiden_clustering(graph: nx.Graph, resolution: float) -> list[list[int]]:
    """
    Applies Leiden clustering to the sentence similarity graph.

    Args:
        graph (nx.Graph): The similarity graph.
        resolution (float): The Leiden clustering resolution parameter.

    Returns:
        List[List[int]]: List of clusters with sentence indices.
    """
    # Convert NetworkX graph to iGraph
    ig_graph = ig.Graph.TupleList(graph.edges(data=False), directed=False)

    # Run Leiden clustering
    partition = leidenalg.find_partition(
        ig_graph, leidenalg.CPMVertexPartition, resolution_parameter=resolution
    )
    clusters = [list(cluster) for cluster in partition]
    return clusters


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
    print(f"resolution: {resolution}")

    # Build similarity graph
    graph = build_similarity_graph(sentences, embeddings, threshold)
    debug_display_graph(graph, embeddings, sentences, threshold=threshold)

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
            merged_chunks.extend([f"[MERGED] {chunk}" for chunk in split_chunks])
        else:
            merged_chunks.append(f"[MERGED] {merged_text}")

    # Include sentences that were not clustered
    all_indices = set(range(len(sentences)))
    clustered_indices = {i for cluster in clusters for i in cluster}
    unclustered_indices = all_indices - clustered_indices

    for idx in unclustered_indices:
        merged_chunks.append(
            f"[SINGLE] {sentences[idx]}"
        )  # Tagging standalone entries for clarity
    return merged_chunks


def compute_dynamic_threshold(
    embeddings: list[np.ndarray],
    percentile: float = 75,
    lower_bound: float = 0.3,
    upper_bound: float = 0.7,
) -> float:
    """
    Computes a threshold by taking the given percentile of all pairwise similarities.
    Clamps the result between lower_bound and upper_bound.

    Args:
        embeddings (List[np.ndarray]): Sentence embeddings.
        percentile (float): Which percentile of the similarity distribution to use.
        lower_bound (float): Minimum allowed threshold.
        upper_bound (float): Maximum allowed threshold.

    Returns:
        float: The dynamic threshold value.
    """
    sim_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()
    # Flatten off-diagonal similarities
    all_sims = []
    n = len(sim_matrix)
    for i in range(n):
        for j in range(i + 1, n):
            all_sims.append(sim_matrix[i][j])

    if len(all_sims) == 0:
        # Edge case: if there's only one sentence or no pairwise combos
        return lower_bound

    raw_threshold = np.percentile(all_sims, percentile)
    # Clamp
    threshold = max(lower_bound, min(raw_threshold, upper_bound))

    print(f"\n=== compute_dynamic_threshold Debug ===")
    print(f"Percentile : {percentile}")
    print(f"Raw        : {raw_threshold:.4f}")
    print(f"Clamped    : {threshold:.4f}")
    print("=======================================\n")

    return threshold
