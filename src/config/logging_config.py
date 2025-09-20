"""
Logging Configuration

Loads logging configuration from YAML.
Supports console and rotating file logging with customizable levels and formats.
"""
# Import libraries
import os
import logging
import logging.config
import yaml

DEFAULT_YAML_PATH = os.path.join(os.path.dirname(__file__), "logging_config.yaml")

def setup_logging(yaml_path: str = DEFAULT_YAML_PATH):
    """
    Set up a logging configuration using a YAML file.
    """
    if not os.path.exists(os.path.dirname(DEFAULT_YAML_PATH)):
        os.makedirs(os.path.dirname(DEFAULT_YAML_PATH), exist_ok=True)
    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
    logging.getLogger(__name__).info("Logging initialized successfully.")