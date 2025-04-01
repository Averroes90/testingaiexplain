import stanza

stanza.download("en")  # This downloads the English models if you haven't already
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse,constituency")
import re


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

            # Check 4 (example): Ensure sentence has words.
            if not getattr(sent, "words", []):
                return False

        return True
    except Exception:
        return False
