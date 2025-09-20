"""
Sentiment Analysis Node

This module is responsible for analyzing the sentiment of cryptocurrency news articles.
It processes news items, evaluates their sentiment (positive, negative, or neutral),
determines their importance level, and assesses market relevance using OpenAI's language model.

Author: Peyman Kh
Date: 2023-03-20
"""
# Import libraries
import logging
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from src.config.config import config
from src.prompts import sentiment_analysis_prompt
from src.state import GraphState, ProcessedNewsItem, Sentiment, Importance

logger = logging.getLogger(__name__)


class ResponseOutputSchema(BaseModel):
    sentiment: Sentiment = Field(
        ...,
        description="Sentiment of the news item. can be positive, negative, or neutral"
    )
    importance: Importance = Field(
        ...,
        description="Importance of the news item. can be low, medium, or high"
    )
    is_market_relevant: bool = Field(
        ...,
        description="Whether the news item is market relevant"
    )


def sentiment_analysis_node(state: GraphState):
    """
    This node performs sentiment analysis on the news items.
    """
    # Check if raw news is empty
    if len(state.unseen_news) == 0:
        logger.error("No unseen news found in the state. Aborting.")
        return {}

    news = state.unseen_news
    model = ChatOpenAI(model=config.model_name, api_key=config.model_api_key.get_secret_value())

    # Add structured output to the model
    structured_model = model.with_structured_output(ResponseOutputSchema)

    logger.info(f"Processing {len(news)} news items...")

    processed_news = []
    for item in news:
        try:
            # Create prompt
            prompt = sentiment_analysis_prompt.invoke({"title": item.title, "text": item.text})
            response = structured_model.invoke(prompt)

            processed_news.append(ProcessedNewsItem(
                id=item.id,
                title=item.title,
                text=item.text,
                source_name=item.source_name,
                news_url=item.news_url,
                image_url=item.image_url,
                sentiment=response.sentiment,  # New field
                importance=response.importance,  # New field
                is_market_relevant=response.is_market_relevant,  # New field
                timestamp=item.timestamp,
            ))

            logger.info(f"Successfully processed news item: {item.id}")
        except Exception as e:
            logger.error(f"Failed to process news item: {e}")
            continue

    # Save processed news to state
    return {"processed_news": processed_news}
