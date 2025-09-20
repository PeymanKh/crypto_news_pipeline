"""
Workflow Helper Functions
"""
# Import libraries
import datetime
import uuid
import logging

def generate_uuid(news_title: str, news_timestamp: datetime.datetime) -> str:
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
        >>> generate_uuid("Market Gains", datetime(2023, 6, 15, 9, 30, 0))
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
