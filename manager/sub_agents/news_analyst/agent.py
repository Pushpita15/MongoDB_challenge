from google.adk.agents import Agent
from google.adk.tools import google_search

news_analyst = Agent(
    name="news_analyst",
    model="gemini-2.0-flash",
    description="News analyst agent",
    instruction="""
    You are a helpful assistant that can analyze news articles and provide a summary of the news.

    When asked about news, you should use the google_search tool to search for the news.

    If the user asks for a specific topic, you should search for news articles related to that topic and provide a summary of the articles.
    
    If the user asks for a specific news article, you should search for that article and provide a summary of the article.

    Display the summary of the result in the chat.
    """,
    tools=[google_search],
)
