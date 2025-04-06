from chunking.grammar_check import is_merged_grammatical
import stanza

stanza.download("en")  # This downloads the English models if you haven't already
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse,constituency")


def merge_line_chunks(lines_with_features: list[dict], nlp=nlp) -> list[str]:
    """
    Merges lines into coherent chunks based on rule-based priorities and grammatical validation.

    :param lines_with_features: A list of dictionaries containing lines and associated features.
    :param nlp: Stanza pipeline instance with constituency parsing enabled.
    :return: A list of merged line strings.
    """
    merged_lines = []
    i = 0
    n = len(lines_with_features)

    while i < n:
        current_chunk_lines = [lines_with_features[i]["line"].strip()]
        j = i + 1

        while j < n:
            prev_line = lines_with_features[j - 1]
            next_line = lines_with_features[j]
            # print(f"i is {i}")
            # print(f"prev. line {prev_line}")
            # print(f"next line {next_line}")
            # print(f"current chunk {current_chunk_lines}")

            # Check rules in order of priority

            # Rule 1: bullet on next line
            if next_line["contains_bullet"]:
                break

            # Rule 2: conjunction-based merge
            if (
                prev_line["ends_with_conjunction"]
                or next_line["starts_with_conjunction"]
            ):
                current_chunk_lines.append(next_line["line"].strip())
                j += 1
                continue

            # Rule 3: section header presence
            if prev_line["is_section_header"] or next_line["is_section_header"]:
                break

            # Rule 4: visual separation on first line only
            if len(current_chunk_lines) == 1 and prev_line["is_visually_separated"]:
                break

            # Rule 5: contact info on first or next line
            if len(current_chunk_lines) == 1 and (
                prev_line["contains_contact_info"] or next_line["contains_contact_info"]
            ):
                break

            if prev_line["is_section_header"] or next_line["is_section_header"]:
                break

            # Rule 6: only company line or school in first or next line
            if (
                prev_line["zero_shot_classification"]["label"]
                in ["COMPANY LINE", "EDUCATION"]
                and any(
                    ent["label"] == "ORG"
                    for ent in prev_line["named_entity_recognition"]
                )
            ) or (
                next_line["zero_shot_classification"]["label"]
                in ["COMPANY LINE", "EDUCATION"]
                and any(
                    ent["label"] == "ORG"
                    for ent in next_line["named_entity_recognition"]
                )
            ):
                break

            if (
                prev_line["is_visually_separated"]
                and next_line["is_visually_separated"]
            ):
                break

            current_chunk_lines.append(next_line["line"].strip())
            j += 1

        # Rule 6 (part b): if chunk has 2+ lines and we hit a stop rule, validate grammatically
        while len(current_chunk_lines) > 1 and not is_merged_grammatical(
            " ".join(current_chunk_lines), nlp
        ):
            print(f"is not grammatical ......{current_chunk_lines}")
            current_chunk_lines.pop()  # remove last merged line
            j -= 1  # move pointer back accordingly

        merged_lines.append(" ".join(current_chunk_lines))
        i = j

    return merged_lines
