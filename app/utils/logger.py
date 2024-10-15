import logging
import os

def setup_logger(name, log_file="app.log", level=logging.DEBUG):
    """Function to set up a logger."""
    
    # Create logs directory if it doesn"t exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create file handler to write logs to a file
    file_handler = logging.FileHandler(os.path.join("logs", log_file))
    file_handler.setLevel(level)

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create a default logger for the application
app_logger = setup_logger("app_logger")
source_logger = setup_logger("source_logger", log_file="sources.log", level=logging.DEBUG)