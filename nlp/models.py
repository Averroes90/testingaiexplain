import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
from custom_debugging import debug_display_graph
import networkx as nx
import leidenalg
import igraph as ig

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Load a high-quality sentence embedding model
# model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and accurate

model = SentenceTransformer("all-mpnet-base-v2")  # Best accuracy
# or
# model = SentenceTransformer("all-distilroberta-v1")  # Speed & accuracy balance
# # or
# model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")  # Thematic clustering


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

    # print(f"\n=== compute_dynamic_threshold Debug ===")
    # print(f"Percentile : {percentile}")
    # print(f"Raw        : {raw_threshold:.4f}")
    # print(f"Clamped    : {threshold:.4f}")
    # print("=======================================\n")

    return threshold


def find_best_label_by_embeddings(
    line: str, synonyms_map: dict[str, list[str]], threshold: float = 0.85
) -> list[dict]:
    """
    Computes embedding-based similarities for the input line across
    all canonical labels and their surface forms/synonyms.

    Steps:
      1. Embeds the input line
      2. For each canonical_label in synonyms_map:
         - Embeds all of its surface forms (including the canonical label itself)
         - Computes the individual cosine similarities between the line embedding
           and each surface form embedding
         - Computes the average similarity
      3. Collects these results in a list of dicts, sorted by average similarity (descending).

    :param line: The input text line
    :param synonyms_map: A dict of the form:
        {
          "PROFESSIONAL EXPERIENCE": ["professional experience", "work experience", "employment history", ...],
          "EDUCATION": ["education", "academic background", "educational qualifications", ...],
          ...
        }
    :param threshold: Only include labels whose average similarity >= this threshold
    :return: A list of dicts. Each dict has:
       {
         "canonical_label": str,
         "average_similarity": float,
         "synonyms": [
             {"text": str, "similarity": float},
             ...
         ]
       }
      The list is sorted in descending order of average_similarity.
    """

    # Encode the input line
    line_embedding = model.encode(line, convert_to_tensor=True)

    results = []

    # Compare the line embedding with each canonical_label's surface forms
    for canonical_label, surface_forms in synonyms_map.items():
        # Encode all synonyms
        surface_embeddings = model.encode(surface_forms, convert_to_tensor=True)

        # shape: (1 x num_surface_forms) => [num_surface_forms]
        cos_scores = util.cos_sim(line_embedding, surface_embeddings)[0].cpu().numpy()

        # Build a list of individual synonyms and their similarity
        individual_synonyms = []
        for syn_text, score in zip(surface_forms, cos_scores):
            individual_synonyms.append({"text": syn_text, "similarity": float(score)})

        # Compute average similarity across all synonyms
        average_similarity = float(np.mean(cos_scores))

        # Store in a structured format
        results.append(
            {
                "canonical_label": canonical_label,
                "average_similarity": average_similarity,
                "synonyms": individual_synonyms,
            }
        )

    # Sort all results in descending order by average_similarity
    results.sort(key=lambda x: x["average_similarity"], reverse=True)

    # Optionally filter out those below threshold
    filtered_results = [r for r in results if r["average_similarity"] >= threshold]

    return filtered_results
