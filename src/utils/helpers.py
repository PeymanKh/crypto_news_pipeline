"""
Workflow Helper Functions
"""
# Import libraries
import uuid
import logging
import requests
import datetime
from typing import Optional, Dict, Any

from src.state import ProcessedNewsItem
from src.config.config import config
logger = logging.getLogger(__name__)


def generate_unique_id(news_title: str, news_timestamp: datetime.datetime) -> str:
    """
    Generate a deterministic UUID5 based on news title and timestamp.

    Creates a unique identifier that remains consistent for the same news item
    across processing runs. Uses UUID5 (SHA-1 hash) for deterministic generation.

    Args:
        news_title: Title of the news article
        news_timestamp: Publication timestamp of the article (datetime object)

    Returns:
        str: Deterministic UUID string

    Raises:
        TypeError: If inputs are not correct types
        ValueError: If inputs are empty or invalid
        UUIDGenerationError: If UUID generation fails

    Example:
        >>> from datetime import datetime
        >>> generate_unique_id("Market Gains", datetime(2023, 6, 15, 9, 30, 0))
        '95383fac-db29-5885-9168-0553ae2e64aa'
    """
    try:
        # Sanitize inputs
        title_clean = news_title.strip()
        # Convert datetime to ISO format string for consistent hashing
        timestamp_str = news_timestamp.isoformat()

        # Create a unique composite key
        composite_key = f"{title_clean}-{timestamp_str}"
        logging.debug(f"Generated composite key for UUID: {composite_key[:50]}...")

        # Parse namespace UUID
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

        # Generate deterministic UUID5
        generated_uuid = str(uuid.uuid5(namespace, composite_key))
        logging.debug(f"Successfully generated UUID: {generated_uuid}")

        return generated_uuid

    except Exception as e:
        logging.exception(f"Unexpected error during UUID generation: {str(e)}")
        raise


def _build_telegram_message(news: ProcessedNewsItem) -> str:
    """
    Build a beautifully formatted Telegram message from news data.
    """
    try:
        # Extract data with fallbacks
        title = news.title.strip() if news.title else "📰 Crypto News"
        text = news.text.strip() if news.text else "No content available"
        sentiment = news.sentiment.value.capitalize() if news.sentiment else "Unknown"
        importance = news.importance.value.capitalize() if news.importance else "Unknown"
        source = news.source_name.strip() if news.source_name else "Unknown Source"
        url = news.news_url.strip() if news.news_url else ""

        # Choose emoji based on sentiment
        sentiment_emoji = {
            "positive": "🟢",
            "negative": "🔴",
            "neutral": "🟡"
        }.get(sentiment.lower(), "⚪")

        # Choose emoji based on importance
        importance_emoji = {
            "high": "🔥",
            "medium": "⚡",
            "low": "💡"
        }.get(importance.lower(), "📊")

        # Truncate text if too long (keep under 300 chars for readability)
        if len(text) > 300:
            text = text[:297] + "..."

        # Build clean message
        message_parts = [
            f"📈 **{title}**",
            "",  # Empty line for spacing
            f"_{text}_",
            "",  # Empty line for spacing
            f"{sentiment_emoji} **Sentiment:** {sentiment}",
            f"{importance_emoji} **Impact:** {importance}",
            "",  # Empty line before source
        ]

        # Add source with better formatting
        if url and url.startswith(('http://', 'https://')):
            message_parts.append(f"📰 [Read More on {source}]({url})")
        else:
            message_parts.append(f"📰 **Source:** {source}")

        # Add separator
        message_parts.append("─────────────────")

        full_message = "\n".join(message_parts)

        return full_message

    except Exception as e:
        logger.error(f"Failed to build Telegram message: {str(e)}")
        raise


def send_telegram_message(news: ProcessedNewsItem) -> Optional[Dict[str, Any]]:
    """
    Sends a news article to the 'Haberler' forum topic in the Jön Traderlar Telegram group.

    Args:
        news: ProcessedNews containing news details

    Returns:
        Optional[Dict]: Response from the Telegram API, None if failed
    """
    try:
        # Build message
        full_message = _build_telegram_message(news)

        # Prepare API request
        send_message_url = f"https://api.telegram.org/bot{config.bot_token.get_secret_value()}/sendMessage"

        payload = {
            "chat_id": config.group_id.get_secret_value(),
            "text": full_message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }

        # Send request to telegram
        try:
            response = requests.post(
                send_message_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            logger.error(f"Failed to send message to Telegram: {str(e)}")
            raise

        # Handle response
        if response.status_code == 200:
            logger.info("Message sent successfully to Telegram")

    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {str(e)}")
        return {}