import logging
import logging.handlers
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    # Rotating file handler
    fh = logging.handlers.RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"), maxBytes=5 * 1024 * 1024, backupCount=5
    )
    fh.setLevel(level)
    fh.setFormatter(formatter)

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(level)
        root.addHandler(ch)
        root.addHandler(fh)


def get_logger(name: str):
    configure_logging()
    return logging.getLogger(name)
