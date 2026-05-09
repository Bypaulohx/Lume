"""
Logging configuration for Lume V2.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "lume", log_dir: str = "lume/logs", level=logging.INFO) -> logging.Logger:
    """
    Configure and return a logger for Lume.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"lume_{timestamp}.log"
    
    # File handler (detailed)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler (less verbose)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
