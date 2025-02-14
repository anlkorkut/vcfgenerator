"""This module contains the logger initialization function."""
import os
import logging
import inspect
from env import LOG_LEVEL, LOG_FOLDER

def init(name):
    """Initialize a logger with the given name and returns it."""

    # Get the logger with the provided name
    logger = logging.getLogger(name)

    # Return existing logger if it already has handlers
    if logger.hasHandlers():
        return logger

    # Set the logger level from environment variable
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    # Get the caller's filename using inspect
    caller_frame = inspect.stack()[1]
    caller_filename = caller_frame.filename

    # Extract the filename without extension to use as log file name
    current_filename_without_ext = os.path.splitext(os.path.basename(caller_filename))[0]

    # Create log folder if it doesn't exist
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    # Construct the full log file path
    log_filename = os.path.join(LOG_FOLDER, f"{current_filename_without_ext}.log")

    # Set up the file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

    # Set up the formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger