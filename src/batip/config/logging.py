import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level}</level> | "
           "{message}"
)

logger.add(
    "logs/batip.log",
    rotation="10 MB",
    retention="10 days",
    level="DEBUG"
)