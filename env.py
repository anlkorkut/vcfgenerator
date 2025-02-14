"""Environment variables for the application."""
import os

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FOLDER = "logs"

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
