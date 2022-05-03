import os
import logging


level = logging.DEBUG if os.environ.get("DEBUG") else logging.WARNING

logging.basicConfig(level=level)
