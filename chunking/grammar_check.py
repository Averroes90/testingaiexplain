import stanza

stanza.download("en")  # This downloads the English models if you haven't already
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse,constituency")
import re


def check_consecutive_sus_phrases(sent, threshold: int = 6) -> bool:
    """
    Checks for a trailing sequence of 'suspect' tokens in the sentence's words, iterating backwards.
    Originally, tokens with POS tags PROPN, NOUN, and NUM were flagged. Now, we remove NUM from the suspect
    set and instead only flag numbers that match date patterns (e.g. a four-digit year or a full date format).

    The count resets when a proper separator is encountered. Tokens like hyphens and brackets are ignored.

    Returns True if the sentence passes the check (i.e. does not contain consecutive suspect tokens above
    the threshold), otherwise False.
    """
    # Suspect tokens now only include proper nouns and common nouns.
    sus_tags = {"PROPN", "NOUN"}
    # Tokens that indicate proper structure (or punctuation that should reset the count)
    proper_separators = {"PUNCT", "CCONJ", "VERB"}
    # Specific token texts to ignore
    ignored_tokens = {"-", "–", "(", ")", "[", "]", "{", "}"}
    # Tags to ignore entirely
    ignored_tags = {"ADJ"}

    # Regular expressions for date detection:
    year_pattern = re.compile(r"^\d{4}$")  # Matches a standalone year, e.g. "2020"
    # A simple pattern for a full date (e.g., "12/31/2020" or "12-31-2020")
    full_date_pattern = re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$")

    count = 0
    for word in reversed(getattr(sent, "words", [])):
        # Skip tokens that are explicitly ignored.
        print(f"word {word.text}")
        print(f"pos {word.pos}")
        if word.text in ignored_tokens or (
            hasattr(word, "pos") and word.pos in ignored_tags
        ):
            continue

        # Reset counter when encountering punctuation (commas, periods) or proper separators.
        if word.text in {",", "."} or (
            hasattr(word, "pos") and word.pos in proper_separators
        ):
            # make sure the sequence is at least one token removed from a verb
            if hasattr(word, "pos") and word.pos in {"VERB", "AUX"}:
                count -= 1
            else:
                count = 0
            continue

        if hasattr(word, "pos"):
            if word.pos == "NUM":
                # Only consider the number suspect if it matches a date pattern.
                if year_pattern.match(word.text) or full_date_pattern.match(word.text):
                    count += 1
                    print(f"count {count}")
                    if count >= threshold:
                        return False
                else:
                    # Numbers that are not dates are not flagged, so reset count.
                    count = 0
                continue
            elif word.pos in sus_tags:
                count += 1
                print(f"count {count}")
                if count >= threshold:
                    return False
            else:
                # Any other POS resets the counter.
                count = 0
        else:
            count = 0
    return True


def is_merged_grammatical(text: str, nlp=nlp) -> bool:
    try:
        doc = nlp(text)
        if not doc.sentences:
            return False

        for sent in doc.sentences:
            # Skip sentences without constituency info.
            if not sent.constituency:
                continue

            tree_str = str(sent.constituency).strip()

            # Check 1: Sentence root structure.
            # Must start with a valid root; otherwise, if it contains an NP with an S, fail.
            if not (
                tree_str.startswith("(ROOT (S")
                or tree_str.startswith("(ROOT (SINV")
                or tree_str.startswith("(ROOT (SBAR")
            ):
                if re.search(r"\(NP\s+\(S[\s\)]", tree_str):
                    return False

            # Check 2: NFP (allowed only at the beginning).
            nfp_index = tree_str.find("NFP")
            if nfp_index != -1:
                first_nfp = re.search(r"\(NFP\b", tree_str)
                if first_nfp and first_nfp.start() > 30:
                    return False

            # Check 3: Reject if any unwanted tags are present.
            if "ADD" in tree_str or "EMAIL" in tree_str or "URL" in tree_str:
                return False

            # Check 4: Ensure sentence has words.
            if not getattr(sent, "words", []):
                return False

            # New Check 5: Look for excessive consecutive "sus" tokens (from the end backwards).
            # If check fails, the merged text likely contains improperly merged content.
            if not check_consecutive_sus_phrases(sent):
                return False

        return True
    except Exception:
        return False
