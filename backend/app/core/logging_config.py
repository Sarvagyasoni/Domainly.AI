import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """
    Configures logging for the whole app.
    Call this once, at startup, from main.py.

    Logs go to two places:
    - Console (so you still see them while developing)
    - backend/logs/app.log (so they survive after you close the terminal)
    """
    logs_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    file_handler = RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=1_000_000,   # rotate after ~1MB so the file doesn't grow forever
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
