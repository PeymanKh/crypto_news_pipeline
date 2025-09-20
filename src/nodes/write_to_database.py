"""
Database Write Node

This module is responsible for saving processed news items to the database.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging

from src.state import GraphState
from src.utils.db_utils import add_bulk_news

logger = logging.getLogger(__name__)


def write_to_database_node(state: GraphState):
    """
    This node is responsible for adding processed news items to the database.
    **Note: Failure is handled by add_bulk_news function in utils/db_utils.**
    """
    processed_news = state.processed_news

    if not processed_news:
        logger.info("No new items for database write")
        return {}

    result = add_bulk_news(processed_news)

    if result:
        logger.info(f"Successfully added {len(result)} news items to the database.")
        return {"database_write_success": True}

    return {"database_write_success": False}