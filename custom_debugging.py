import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def debug_display_graph(
    G: nx.Graph,
    embeddings: list[np.ndarray],
    sentences: list[str],
    threshold: float = None,
):
    """
    Debug function to display a 2D visualization of your existing similarity graph.
    - Does NOT compute edges (they're already in G).
    - Uses PCA to reduce your embeddings to 2D, then applies a spring layout.
    - Labels each node by index and prints a reference index -> sentence.

    Args:
        G (nx.Graph): Already built similarity graph (from build_similarity_graph).
        embeddings (List[np.ndarray]): The same embeddings used to build G.
        sentences (List[str]): The same sentences used to build G.
        threshold (float, optional): Just for displaying in the title, if you want.
    """

    # 1. Get all node indices from the graph
    node_indices = sorted(G.nodes())

    # 2. Reduce embeddings to 2D for initial layout via PCA
    pca = PCA(n_components=2)
    coords_2d = pca.fit_transform(embeddings)
    initial_pos = {i: coords_2d[i] for i in node_indices}

    # 3. Apply a spring layout to space nodes out nicely
    #    'pos=initial_pos' starts the spring layout from PCA positions
    pos = nx.spring_layout(G, pos=initial_pos, iterations=50)

    # 4. Draw the nodes and edges
    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=500)
    nx.draw_networkx_edges(G, pos, alpha=0.3)

    # Label each node with its index, to keep the plot readable
    labels = {i: str(i) for i in node_indices}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    # 5. Annotate the plot
    if threshold is not None:
        plt.title(f"Sentence Graph (Threshold={threshold})")
    else:
        plt.title("Sentence Graph (Threshold not provided)")
    plt.axis("off")
    plt.show()

    # 6. Print a legend for reference: index -> original sentence
    print("\nNODE REFERENCE:")
    for i in node_indices:
        print(f"[{i}] {sentences[i]}\n")
