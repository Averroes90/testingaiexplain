import json
from chunking.chunk_free_form import model


def coarse_segmentation(
    lines: list,
    window_size: int = 5,
    threshold: float = 0.05,
    smooth_features: bool = True,
    feature_inclusion: dict = None,
):
    """
    Performs coarse segmentation on resume lines.

    Parameters:
      - lines: List of line dictionaries.
      - window_size: Size of the sliding window for smoothing.
      - threshold: Distance threshold for change point detection.
      - smooth_features: Whether to apply smoothing to the feature vectors.
      - feature_inclusion: Dictionary specifying which features to include.
         Example: {"zsc": True, "ner": True, "formatting": True, "embedding": False}

    Returns:
      - boundaries: A list of indices (line numbers) where change points are detected.
    """
    # Default feature inclusion settings if not provided.
    if feature_inclusion is None:
        feature_inclusion = {
            "zsc": True,
            "ner": True,
            "formatting": True,
            "embedding": False,
        }

    features = []
    for line in lines:
        zsc = extract_zsc(line)
        ner = extract_ner(line)
        formatting = extract_formatting(line)
        embedding = model.encode(
            line["line"]
        )  # Uncomment if you have an embedding function.
        # For now, we'll assume no embedding.
        composite_vector = combine_features(
            zsc,
            ner,
            formatting,
            embedding=embedding,
            feature_inclusion=feature_inclusion,
        )
        features.append(composite_vector)

    # Optionally smooth the feature signal.
    if smooth_features:
        smoothed_features = smooth(features, window_size=window_size)
    else:
        smoothed_features = features

    # Detect change points on the (smoothed) feature vectors.
    boundaries = detect_change_points(smoothed_features, threshold=threshold)

    return boundaries


def combine_features(
    zsc: dict,
    ner: dict,
    formatting: dict,
    embedding=None,
    feature_inclusion: dict = None,
):
    """
    Combines multiple signals into a composite feature vector.

    Parameters:
      - zsc: Dictionary with zero-shot classification output.
      - ner: Dictionary with NER counts.
      - formatting: Dictionary with formatting cues.
      - embedding: Optional semantic embedding vector.
      - feature_inclusion: Dict controlling which components to include.
         Example: {"zsc": True, "ner": True, "formatting": True, "embedding": False}

    Returns:
      - composite_vector: A list (vector) combining selected features.
    """
    # Set default feature inclusion if not provided.
    if feature_inclusion is None:
        feature_inclusion = {
            "zsc": True,
            "ner": True,
            "formatting": True,
            "embedding": False,
        }

    composite_vector = []

    # -- ZSC Features --
    if feature_inclusion.get("zsc", True):
        composite_vector.append(zsc.get("confidence", 0))
        # Assume one_hot_encode returns a list.
        label_one_hot = one_hot_encode(
            zsc.get("label", ""),
            label_vocab=["JOB TITLE", "COMPANY LINE", "PROFESSIONAL EXPERIENCE"],
        )
        composite_vector.extend(label_one_hot)

    # -- NER Features --
    if feature_inclusion.get("ner", True):
        composite_vector.append(ner.get("count_org", 0))
        composite_vector.append(ner.get("count_loc", 0))
        composite_vector.append(ner.get("count_per", 0))

    # -- Formatting Features --
    if feature_inclusion.get("formatting", True):
        composite_vector.append(1 if formatting.get("is_bullet", False) else 0)
        composite_vector.append(1 if formatting.get("is_all_caps", False) else 0)
        composite_vector.append(1 if formatting.get("has_colon", False) else 0)

    # -- Optional Embedding --
    if feature_inclusion.get("embedding", False) and embedding is not None:
        composite_vector.extend(embedding)

    return composite_vector


def one_hot_encode(label: str, label_vocab: list):
    """
    Convert a label into a one-hot encoded vector based on a given vocabulary.

    Parameters:
        label (str): The label to encode.
        label_vocab (list of str): The list of possible labels.

    Returns:
        list: A one-hot encoded vector (list of integers).
    """
    # Initialize the vector with zeros.
    one_hot_vector = [0] * len(label_vocab)

    # Try to find the label in the vocabulary.
    try:
        index = label_vocab.index(label)
        one_hot_vector[index] = 1
    except ValueError:
        # If the label is not found, the vector remains all zeros.
        pass

    return one_hot_vector


def get_label_vocab(json_file_path: str = "config/labels.json"):
    """
    Reads a JSON file from the given directory and extracts the list of canonical labels.

    Parameters:
        json_file_path (str): The file path to the JSON file.

    Returns:
        list: A list of canonical labels.
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract canonical labels from the "labels" list
    labels_list = data.get("labels", [])
    canonical_labels = [
        entry.get("canonical_label")
        for entry in labels_list
        if entry.get("canonical_label")
    ]

    return canonical_labels


def extract_zsc(line: dict):
    """
    Extract the zero-shot classification (ZSC) features from the line.

    Returns a dictionary with:
      - 'label': The predicted label (or None if missing).
      - 'confidence': The associated confidence score (default 0 if missing).
    """
    zsc_data = line.get("zero_shot_classification", {})
    return {
        "label": zsc_data.get("label", None),
        "confidence": zsc_data.get("score", 0),
    }


def extract_ner(line: dict):
    """
    Extract NER counts from the line.

    Returns a dictionary with counts for key entity types:
      - 'count_org': Count of organization entities.
      - 'count_loc': Count of location entities.
      - 'count_per': Count of person entities.
    """
    ner_list = line.get("named_entity_recognition", [])
    counts = {"count_org": 0, "count_loc": 0, "count_per": 0}
    for entity in ner_list:
        entity_label = entity.get("label", "").upper()
        if entity_label == "ORG":
            counts["count_org"] += 1
        elif entity_label == "LOC":
            counts["count_loc"] += 1
        elif entity_label == "PER":
            counts["count_per"] += 1
    return counts


def extract_formatting(line: dict) -> dict:
    """
    Extract formatting features from the line.

    Returns a dictionary with binary indicators for:
      - 'is_visually_separated'
      - 'contains_bullet'
      - 'contains_contact_info'
    """
    return {
        "is_visually_separated": 1 if line.get("is_visually_separated", False) else 0,
        "contains_bullet": 1 if line.get("contains_bullet", False) else 0,
        "contains_contact_info": 1 if line.get("contains_contact_info", False) else 0,
    }


def smooth(features: list, window_size: int = 5) -> list:
    """
    Smooth a list of composite feature vectors using a sliding window average.

    Parameters:
        features (list of list of float): Composite feature vectors for each line.
        window_size (int): The number of consecutive vectors to average.

    Returns:
        list of list of float: A list of smoothed feature vectors.
    """
    smoothed = []
    half_window = window_size // 2
    num_features = len(features)

    for i in range(num_features):
        # Determine the window range, ensuring we don't go out of bounds.
        start = max(0, i - half_window)
        end = min(num_features, i + half_window + 1)

        # Initialize an average vector with the same dimension as a feature vector.
        avg_vector = [0] * len(features[i])
        count = end - start

        # Sum up vectors within the window.
        for j in range(start, end):
            for k, val in enumerate(features[j]):
                avg_vector[k] += val

        # Compute the average for each dimension.
        avg_vector = [x / count for x in avg_vector]
        smoothed.append(avg_vector)

    return smoothed


import numpy as np
import math


def vector_distance(vec1, vec2):
    """Compute the Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


def detect_change_points(smoothed_features, threshold=0.05):
    """
    Detect change points in a sequence of smoothed feature vectors.

    Parameters:
        smoothed_features (list of list of float): The smoothed composite feature vectors.
        threshold (float): A threshold distance that, when exceeded between adjacent vectors,
                           indicates a change point.

    Returns:
        list of int: Indices where change points are detected.
    """
    distances = []
    for i in range(1, len(smoothed_features)):
        dist = vector_distance(smoothed_features[i], smoothed_features[i - 1])
        distances.append(dist)

    if distances:
        avg_dist = np.mean(distances)
        min_dist = np.min(distances)
        max_dist = np.max(distances)
        percentiles = np.percentile(distances, [25, 50, 75])
        print("Distance Statistics:")
        print(f"  Average:          {avg_dist:.4f}")
        print(f"  Minimum:          {min_dist:.4f}")
        print(f"  Maximum:          {max_dist:.4f}")
        print(f"  25th Percentile:  {percentiles[0]:.4f}")
        print(f"  Median:           {percentiles[1]:.4f}")
        print(f"  75th Percentile:  {percentiles[2]:.4f}")
    else:
        print("No distances computed (insufficient features).")

    change_points = []
    for i, dist in enumerate(distances, start=1):
        if dist > threshold:
            change_points.append(i)

    return change_points
