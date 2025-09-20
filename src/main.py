
# Import libraries
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from src.state import GraphState
from src.config.logging_config import setup_logging
from src.nodes.fetch_news import fetch_news_node
from src.nodes.check_cache import check_cache_node
from src.nodes.sentiment_analysis import sentiment_analysis_node
from src.nodes.write_to_database import write_to_database_node
from src.nodes.telegram_notifier import notification_node

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def create_graph():
    # Build graph
    builder = StateGraph(GraphState)
    builder.add_node("fetch_news", fetch_news_node)
    builder.add_node("check_cache", check_cache_node)
    builder.add_node("analyze_sentiment", sentiment_analysis_node)
    builder.add_node("write_to_database", write_to_database_node)
    builder.add_node("telegram_notifier", notification_node)

    builder.add_edge(START, "fetch_news")
    builder.add_edge("fetch_news", "check_cache")
    builder.add_edge("check_cache", "analyze_sentiment")
    builder.add_edge("analyze_sentiment", "write_to_database")
    builder.add_edge("analyze_sentiment", "telegram_notifier")
    builder.add_edge("write_to_database", END)
    builder.add_edge("telegram_notifier", END)

    return builder


if __name__ == "__main__":
    graph_builder = create_graph()

    memory = InMemorySaver()
    graph = graph_builder.compile(memory)

    thread = {"configurable": {"thread_id": "test"}}
    initial_state = GraphState(raw_news=[], cache=[], cache_hit=0, unseen_news=[], processed_news=[],
                               database_write_success=False, telegram_notification_success=False)

    result = graph.invoke(initial_state, thread)
