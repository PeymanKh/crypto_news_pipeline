"""
Graph State Schema

This module Defines schemas for news items at different processing stages and the overall graph state.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel


class Sentiment(str, Enum):
    """Sentiment categories for news items"""
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class Importance(str, Enum):
    """Importance categories for news items"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class NewsItem(BaseModel):
    """Single news item schema from the news API"""
    id: str
    title: str
    text: str
    source_name: str
    news_url: str
    image_url: str
    timestamp: datetime.datetime


class ProcessedNewsItem(BaseModel):
    """Single news item schema after processing the news with LLM"""
    id: str
    title: str
    text: str
    source_name: str
    news_url: str
    image_url: str
    sentiment: Sentiment  # New field
    importance: Importance  # New field
    is_market_relevant: bool  # New field
    timestamp: datetime.datetime


class GraphState(BaseModel):
    """Graph state schema"""
    raw_news: List[NewsItem] = []  # Raw news items from the news API
    cache: List[str] = []  # Unique id of cached news items
    cache_hit: int = 0  # Number of news items that were found in the cache
    unseen_news: List[NewsItem] = []  # Unseen news items that were not found in the cache
    processed_news: List[ProcessedNewsItem] = []  # Processed news items
    database_write_success: bool = False  # Flag indicating if the news items were written to the database
    telegram_notification_success: bool = False  # Flag indicating if the news items were sent to Telegram