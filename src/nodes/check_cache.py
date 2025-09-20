"""
Cache Checker Node

This module is responsible for filtering news items against a cache to prevent
duplicate processing. It checks each news item's ID against previously processed
entries and forwards only unseen items for further processing in the pipeline.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging

from src.state import GraphState
from src.utils.db_utils import fetch_cache

logger = logging.getLogger(__name__)


def check_cache_node(state: GraphState):
    """
    This node is used to check if the news items are already in the cache. The reason is to avoid processing the same
    news multiple times with LLM.
    """
    # Check if raw news is empty
    raw_news = state.raw_news

    if not raw_news:
        logger.error("No raw news found in the state. Aborting.")
        return {}

    try:
        cache = fetch_cache()
        logger.info(f"Cache loaded successfully with {len(cache)} items.")

        # Filter unseen news
        unseen_news = []
        cache_hit = 0

        for news in raw_news:
            if not news.id:
                logger.error(f"News item {news} has no ID. Aborting.")
            elif news.id in cache:
                cache_hit += 1
            else:
                unseen_news.append(news)

        # Update state
        return {
            "cache": cache,
            "cache_hit": cache_hit,
            "unseen_news": unseen_news,
        }

    except Exception as e:
        logger.error(f"Failed to check cache: {e}")
        return {}