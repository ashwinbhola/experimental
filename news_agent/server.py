import os
import logging
from datetime import datetime

from typing import Annotated, Literal, Optional
from pydantic import Field

from mcp.server.fastmcp import FastMCP
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# By default, this will set up a handler that outputs to sys.stderr
# that doesn't interfere with the stdin or stdout streams used by MCP
# server and client to communicate
logging.basicConfig(
    level=logging.INFO, 
    format="[MCP_SERVER] %(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the MCP Server
news_server = FastMCP("NewsServer")

# Initialize NewsAPI
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY not found. Please set it in the .env file.")
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# NumStories = Annotated[
#     int, 
#     Field(
#         description="The number of latest summarized news stories to fetch (default: 10, max 100)."
#     )
# ]

Category = Annotated[
    Literal["business", "entertainment", "general", "health", "science", "sports", "technology", None], 
    Field(
        description="The category you want to get headlines for. Default value is None which fetches the stories for all categories."
    )
]

@news_server.tool()
def get_world_news(category: Category = None) -> list[dict]:
    """
    Fetches live news stories (summarized) sorted in reverse by their publish times.
    
    MUST be used to fetch the current, up-to-date headlines and breaking news
    from around the world.
    """

    try:
        request_params = {
            "language": "en",
            "page_size": 50,
        }
        if category:
            request_params["category"] = category
        # Use top-headlines for the most current and major news
        response = newsapi.get_top_headlines(**request_params)

        if response.get("status") != "ok":
            error_msg = response.get("message", "Unknown error")
            logger.warning(f"NewsAPI returned non-OK status: {error_msg}")
            return f"Error fetching news: {error_msg}"
        
        articles = response.get("articles", [])
        
        if not articles:
            return "No major events found at this time."
        
        # Clean the output for the LLM
        cleaned_articles = []
        for article in articles:
            title = article.get("title", None)
            if not title:
                continue 

            description = article.get("description", "")
            source = article["source"].get("name", "Unknown Source")
            time_str = article.get("publishedAt", '')

            # Convert timestamp to a readable format
            try:
                dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                readable_time = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                readable_time = time_str
            
            cleaned_articles.append(
                {
                    "title": title,
                    "description": description,
                    "publish_time": readable_time,
                    "source": source,
                }
            )
        
        return cleaned_articles
    except Exception as exc:
        logging.exception(f"Error in get_world_events: {str(exc)}")
        return f"Failed to fetch events due to an internal server error: {str(exc)}"


if __name__ == "__main__":
    # Runs the server using stdio (Standard Input/Output)
    logger.info("Starting MCP News Server...")
    news_server.run()

