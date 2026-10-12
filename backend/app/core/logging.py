import logging
import re
import sys
from typing import Any

# Patterns to mask sensitive tokens, keys, passwords
SECRET_PATTERNS = [
    re.compile(r"(?i)(password\s*[:=]\s*)[^\s,;&'\"]+"),
    re.compile(r"(?i)(secret\s*[:=]\s*)[^\s,;&'\"]+"),
    re.compile(r"(?i)(token\s*[:=]\s*)[^\s,;&'\"]+"),
    re.compile(r"(?i)(bearer\s+)[a-zA-Z0-9_\-\.]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;&'\"]+"),
]


def mask_secrets(message: str) -> str:
    """Mask secret patterns in string before logging or storage."""
    masked = str(message)
    for pattern in SECRET_PATTERNS:
        masked = pattern.sub(r"\1[REDACTED]", masked)
    return masked


class SafeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        orig = super().format(record)
        return mask_secrets(orig)


def setup_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("modernrx")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            SafeFormatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


logger = setup_logging()
