import logging
import os

def setup_logger(name: str, log_file: str="app.log", level=logging.WARNING) -> logging.Logger:
    """
    Function to set up a logger.
    
    :param name: Name used to differentiate logs
    :param log_file: Filename logs are stored to, inside directory 'logs'
    :param level: Logging level used for the logger

    :return: Logger instance used to create logs entries
    """
    
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