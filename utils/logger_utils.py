# logger_utils.py

import os
from loguru import logger
from pprint import pformat

# 1. Configure the log file location.
#    For instance, place it in the 'logs' directory under the project root.
LOG_FILE_PATH = os.path.join("logs", "debug.log")

# 2. Add the log file as a "sink" for Loguru
#    rotation="10 MB" -> once debug.log reaches 10 MB, it auto-rotates to keep logs manageable
logger.add(LOG_FILE_PATH, rotation="10 MB", encoding="utf-8", enqueue=True)

# Optional: You can set a custom format for log lines here if you like:
# logger.add(LOG_FILE_PATH, format="{time} | {level} | {message}", ...)


def log_anything(variable: any, label: str = "DEBUG"):
    """
    Logs any Python object in a pretty-printed, multiline format.
    - 'variable': the data you want to log (could be dict, list, custom objects, etc.)
    - 'label': a short label or description to identify the variable in the logs.
    """
    # Use pprint to format the variable for readability
    pretty_str = pformat(variable, width=120, indent=2)

    # Log with a DEBUG level.
    # The message includes the label and the multiline string.
    logger.debug(f"{label}:\n{pretty_str}")
