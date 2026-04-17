import logging
import os

def setup_logging(log_file="bot.log"):
    """Sets up logging to both console and a file."""
    
    # Get log level from environment variable (default: INFO)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Create logger
    logger = logging.getLogger("trading_bot")
    logger.setLevel(log_level)

    # Prevent duplicate logs if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize default logger
logger = setup_logging()
