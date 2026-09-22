import logging
from pathlib import Path


LOG_FILE = Path("logs/automation.log")


def setup_logger():
    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger("automation")

    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger() is called again
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger