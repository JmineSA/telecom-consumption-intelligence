"""
Logging configuration and utilities
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..config import CONFIG


def setup_logging():
    """Setup logging configuration"""
    config = CONFIG.logging
    
    # Create logs directory if it doesn't exist
    log_dir = Path(config.file_path).parent
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('telecom_app')
    logger.setLevel(getattr(logging, config.level))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(config.format))
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.file_path,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count
    )
    file_handler.setFormatter(logging.Formatter(config.format))
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    logger = logging.getLogger(f'telecom_app.{name}')
    logger.propagate = True
    return logger


# Initialize logging on import
setup_logging()