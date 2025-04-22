# credits_tracker.py
import os
import csv
from datetime import datetime

# Global counters (span across this run only, unless CSV data is loaded)
TOTAL_CREDITS = 0.0
PROMPT_TOKENS = 0
COMPLETION_TOKENS = 0
TOTAL_TOKENS = 0
INITIALIZED = False  # Tracks whether we've loaded data from CSV in this run

LOG_FILENAME = "logs/usage.csv"


def log_usage(
    credits_used,
    prompt_tokens_used: int = 0,
    completion_tokens_used: int = 0,
    transaction_label: str = "",
    reset_counters: bool = False,
):
    """
    Logs one "API transaction" or usage event, along with updated cumulative credits/tokens.

    Steps:
      1. If not yet initialized or reset_counters=True, load the last line of usage.csv to
         set the global counters to the all-time totals so far (or 0 if no data).
      2. If reset_counters=True, sets global counters to 0 ignoring prior CSV data.
      3. Add new usage to the global counters.
      4. Append a row to usage.csv containing:
         [timestamp, transaction_label, credits_used, tokens_used,
          cumulative_credits, cumulative_tokens]
    """
    global TOTAL_CREDITS, TOTAL_TOKENS, INITIALIZED, COMPLETION_TOKENS, PROMPT_TOKENS
    tokens_used = prompt_tokens_used = completion_tokens_used
    # If user wants to reset mid-run, or if we've not initialized yet,
    # do the "initialization" step
    if reset_counters or not INITIALIZED:
        if reset_counters:
            # Start from zero
            TOTAL_CREDITS = 0.0
            TOTAL_TOKENS = 0
            PROMPT_TOKENS = 0
            COMPLETION_TOKENS = 0
            print("[CREDITS TRACKER] Counters have been reset to 0.")
        else:
            # Load from CSV if it exists
            if os.path.isfile(LOG_FILENAME):
                with open(LOG_FILENAME, mode="r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) > 1:
                        # The last row has the final cumulative totals
                        last_row = rows[-1]
                        try:
                            TOTAL_CREDITS = float(last_row[4])  # cumulative_credits
                            TOTAL_TOKENS = int(last_row[5])  # cumulative_tokens
                            PROMPT_TOKENS = int(last_row[6])
                            COMPLETION_TOKENS = int(last_row[7])
                        except (ValueError, IndexError):
                            pass  # If there's some parsing error, we keep them at 0
        INITIALIZED = True

    # Now we update counters
    TOTAL_CREDITS += credits_used
    PROMPT_TOKENS += prompt_tokens_used
    COMPLETION_TOKENS += completion_tokens_used
    TOTAL_TOKENS += tokens_used

    # Prepare row
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_data = [
        timestamp,
        transaction_label,
        credits_used,
        tokens_used,
        TOTAL_CREDITS,
        TOTAL_TOKENS,
        PROMPT_TOKENS,
        COMPLETION_TOKENS,
    ]

    # Check if CSV file exists (to decide if we need a header)
    file_exists = os.path.isfile(LOG_FILENAME)
    with open(LOG_FILENAME, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "timestamp",
                    "transaction_label",
                    "credits_used",
                    "tokens_used",
                    "cumulative_credits",
                    "cumulative_tokens",
                    "prompt_tokens",
                    "completion_tokens",
                ]
            )
        writer.writerow(row_data)

    print(
        f"[CREDITS TRACKER] Logged => {transaction_label}, "
        f"Credits: {credits_used}, Tokens: {tokens_used}, "
        f"Total Credits: {TOTAL_CREDITS}, Total Tokens: {TOTAL_TOKENS}, Prompt Tokens: {PROMPT_TOKENS}, Completion Tokens: {COMPLETION_TOKENS}"
    )
