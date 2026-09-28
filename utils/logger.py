import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = REPORTS_DIR / "test_execution.log"
ROOT_LOG_FILE = ROOT_DIR / "log.txt"


def get_logger(name: str = "OrangeHRM") -> logging.Logger:
    """
    Configure and return a standardized logger instance with file and console handlers.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Reports Directory File Handler
        file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Root log.txt Handler
        root_file_handler = logging.FileHandler(ROOT_LOG_FILE, mode="a", encoding="utf-8")
        root_file_handler.setLevel(logging.INFO)
        root_file_handler.setFormatter(formatter)
        logger.addHandler(root_file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
