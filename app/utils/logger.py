import logging
import sys

def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    Function to set up a logger. Logs are streamed to stdout. 
    
    :param name: Name used to differentiate logs
    :param level: Logging level used for the logger

    :return: Logger instance used to create logs entries
    """

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a console handler to print logs to the console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger

# Create a default logger for the application
app_logger = setup_logger("app_logger")