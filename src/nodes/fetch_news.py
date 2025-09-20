"""
News Fetcher Node

This module is responsible for retrieving the latest cryptocurrency news from
the cryptonews-api.com. It fetches news articles, parses them into structured
NewsItem objects, and updates the GraphState with the retrieved data.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging
import requests
from typing import List
from datetime import datetime

from src.config.config import config
from src.state import NewsItem, GraphState
from src.utils.helpers import generate_unique_id

logger = logging.getLogger(__name__)


def fetch_news_node(state: GraphState):
    """
    This node fetches the latest cryptocurrency news from https://cryptonews-api.com.

    Returns:
        A list of NewsItem objects or an empty list if an error occurs.
    """
    logger.info("Fetching latest cryptocurrency news...")

    try:
        # Get the latest news from api
        url = f"{config.news_url}&token={config.news_api_key.get_secret_value()}"
        response = requests.get(url)
        response.raise_for_status()
        logger.info("Successfully fetched latest cryptocurrency news.")

        news_list: List[NewsItem] = []

        # Parse news items to create a list of NewsItem objects
        for item in response.json()["data"]:
            try:
                # 1. Converting time string to a datetime object
                timestamp_str = item.get("date")
                timestamp = datetime.strptime(timestamp_str, "%a, %d %b %Y %H:%M:%S %z")

                # 2. Generating a unique ID for each news item
                news_id = generate_unique_id(item.get("title"), timestamp)

                news = NewsItem(
                    id=news_id,
                    title=item.get("title"),
                    text=item.get("text"),
                    source_name=item.get("source_name"),
                    news_url = item.get("news_url"),
                    image_url=item.get("image_url"),
                    timestamp=timestamp,
                )
                news_list.append(news)
            except Exception as e:
                logger.error(f"Failed to parse news item: {e}")
                continue

        # Add news items to the graph state
        return {"raw_news": news_list}

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch latest cryptocurrency news: {e}")
        return {"raw_news": []}
