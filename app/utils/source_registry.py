import os
import importlib
import inspect

from app.sources.base_source import BaseSource
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class SourceRegistry:
    _instances: dict[str, BaseSource] = {}
    
    @classmethod
    def get_instance(cls):
        logger.debug("Getting source instances")
        if not cls._instances:
            cls.load_sources()
        return cls._instances

    @classmethod
    def load_sources(cls):
        logger.debug("Loading and instatiating source instances")
        for filename in os.listdir("app/sources"):
            if filename.endswith(".py") and filename != "base_source.py" and filename != "__init__.py":
                module_name = filename[:-3]  # Strip the .py extension
                module = importlib.import_module(f"app.sources.{module_name}")

                # Inspect the module for classes
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseSource) and obj is not BaseSource:
                        instance = obj() # Instantiate
                        cls._instances[obj.__name__] = instance # Store instatiated sources
