from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.analysis_sector_agent.agent import analysis_sector_agent
from .sub_agents.analysis_country_agent.agent import analysis_country_agent
from .sub_agents.news_analyst.agent import news_analyst

from dotenv import load_dotenv
load_dotenv()
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent:
    - analyst_sector_agent
    - analyst_country_agent

    You also have access to the following tools:
    - news_analyst
    
    """,
    sub_agents=[analysis_sector_agent, analysis_country_agent],
    tools=[
        AgentTool(news_analyst)
        
    ],
)