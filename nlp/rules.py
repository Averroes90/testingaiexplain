import language_tool_python
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import torch
import math
import stanza

# Initialize grammar checker and language model
tool = language_tool_python.LanguageTool("en-US")


# Initialize the Stanza pipeline (includes constituency parsing)
# By default, Stanza might not load the constituency processor. We'll specify it explicitly.
# You only need to do this once; you can do it outside the function if you like.
stanza.download("en")  # This downloads the English models if you haven't already
nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse,constituency")

# Use a small GPT-2 model for speed and decent accuracy
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def compute_perplexity(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = inputs.input_ids.to(device)

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        loss = outputs.loss
        perplexity = math.exp(loss.item())
    return round(perplexity, 2)


def annotate_lines(lines):
    annotated = []
    for line in lines:
        # Grammar/spell error count
        matches = tool.check(line)
        error_count = len(matches)

        # Fluency/perplexity score
        try:
            fluency = compute_perplexity(line)
        except Exception as e:
            fluency = None  # Handle edge cases (e.g. blank or very short lines)

        doc = nlp(line)
        parse_trees = []

        # Stanza can split your line into multiple sentences. We'll gather the parse for each.
        for sent in doc.sentences:
            if sent.constituency:
                # Convert the internal parse tree to a string
                tree_str = str(sent.constituency)
                parse_trees.append(tree_str)
            else:
                parse_trees.append("(NO PARSE RETURNED)")

        # Optional: You could analyze the tree to detect "S" vs. "fragment"
        # For example, check if the top-level label is "S" or "SINV" for each parse.
        # parse_analysis = []
        # for ptree in parse_trees:
        #     # A naive check to see if it has a top-level (S ...
        #     if ptree.strip().startswith("(S "):
        #         parse_analysis.append("Likely a complete sentence")
        #     else:
        #         parse_analysis.append("Possible fragment or non-standard structure")

        # 4. Append all info to your annotation
        annotated.append(
            {
                "line": line,
                "grammar_errors": error_count,
                "fluency_score": fluency,
                "constituency_parses": parse_trees,
                # "parse_analysis": parse_analysis  # if you want to store the naive analysis
            }
        )

    return annotated
