"""
Database Operations Module

This module handles database connections and operations. It includes functions for establishing and closing database
connections, fetching news from the database, and adding news to the database.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database

from src.config.config import config

# Module-level connection (create once, reuse across function calls)
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_database() -> Database:
    """
    Establishes and returns a MongoDB database connection.

    This function uses a module-level client and database instance to ensure
    the connection is established only once (singleton pattern) and reused
    across all function calls, which is an efficient use of connection pooling.

    Returns:
        The MongoDB database object.
    """
    global _client, _db
    if _client is None or _db is None:
        logging.info("Initializing database connection...")
        _client = MongoClient(config.db_uri.get_secret_value())
        _db = _client[config.db_name]
        logging.info("Database connection initialized successfully.")
    return _db


def close_database() -> None:
    """
    Closes the database connection.

    This function should be called during application shutdown to gracefully
    terminate the connection pool and release resources. It's particularly
    useful in containerized environments like Docker.
    """
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logging.info("Database connection closed.")


def fetch_cache() -> list[str]:
    """
    Finds last 20 news and return their _id. It is used to find the news that already processed.

    Returns:

    """
    db = get_database()
    collection = db["news"]

    try:
        cursor = collection.find(
            {},
            {"_id": 1}
        ).sort("timestamp", -1).limit(20)

        cache = [str(doc["_id"]) for doc in cursor]
        logging.info(f"Successfully fetched cache with {len(cache)} items.")

        return cache

    except Exception as e:
        logging.error(f"Failed to fetch cache: {e}")
        return []


def add_bulk_news(news: List[Dict[str, Any]]) -> List[str]:
    """
    Bulk insert processed news into the database.

    Args:
        news: List of documents to insert

    Returns:
        List of inserted IDs (strings)

    Raises:
        ValueError: If the news list is empty,
        BulkWriteError: For batch insertion failures
    """
    # Validate news list
    if isinstance(news, list) and len(news) > 0:
        raise ValueError("News list must not be empty.")

    # Validate each news item
    for news_item in news:
        if not isinstance(news_item, dict):
            raise ValueError("Each news item must be a dictionary.")
        if "_id" not in news_item:
            raise ValueError("Each news item must have an _id field.")

    # Insert news into the database
    db = get_database()
    collection = db["news"]

    try:
        result = collection.insert_many(news)
        logging.info(f"Successfully inserted {len(result.inserted_ids)} news.")
        return result.inserted_ids

    except Exception as e:
        logging.error(f"Failed to insert news: {e}")
        return []