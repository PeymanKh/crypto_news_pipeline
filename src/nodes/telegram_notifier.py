"""
Telegram Notifier Node

This module is responsible for sending news items to Telegram using the Telegram Bot API.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging

from src.state import GraphState
from src.utils.helpers import send_telegram_message

logger = logging.getLogger(__name__)


def notification_node(state: GraphState):
    """
    Sends Telegram notifications in batch with rate limiting
    """
    processed_news = state.processed_news

    if not processed_news:
        logger.info("No new items for Telegram notification")
        return {}

    sent_count = 0
    for news in processed_news:
        try:
            send_telegram_message(news)
            sent_count += 1
        except Exception as e:
            logger.error(f"Telegram failed for {news['_id']}: {str(e)}")

    if sent_count > 0:
        logger.info(f"Successfully sent {sent_count} notifications to Telegram")
        return {"telegram_notification_success": True}

    return {"telegram_notification_success": False}
