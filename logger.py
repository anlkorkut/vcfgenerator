"""This module contains the logger initialization function."""
import os
import logging
import inspect

# Define constants directly
LOG_LEVEL = "INFO"
LOG_FOLDER = "logs"

def init(name):
    """Initialize a logger with the given name and returns it."""

    # Transform __main__ to app for the logger name
    logger_name = "app" if name == "__main__" else name

    # Get the logger with the transformed name
    logger = logging.getLogger(logger_name)

    # Return existing logger if it already has handlers
    if logger.hasHandlers():
        return logger

    # Set the logger level
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    try:
        # Create log folder if it doesn't exist
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)

        # Get the caller's filename using inspect
        caller_frame = inspect.stack()[1]
        caller_filename = caller_frame.filename

        # Extract the filename without extension
        current_filename_without_ext = 'app' if os.path.basename(caller_filename) == '__main__.py' else os.path.splitext(os.path.basename(caller_filename))[0]

        # Construct the full log file path
        log_filename = os.path.join(LOG_FOLDER, f"{current_filename_without_ext}.log")

        # Set up the file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        # Set up the formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)
    except Exception as e:
        # If we can't create file handler, just use stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(stream_handler)
        logger.warning(f"Could not create file handler: {str(e)}")

    return logger