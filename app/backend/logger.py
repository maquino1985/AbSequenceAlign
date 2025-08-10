import logging
import os
import sys

if "pytest" in sys.modules:
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app-test.log")
else:
    LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Avoid adding handlers multiple times
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
