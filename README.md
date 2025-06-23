# Carbon Emission Analysis agent
This project aims to develop an agent that analyses Carbon emission data . The agent analyses the carbon emission from different industrial sectors and countries, and also it is capable of providing latest news on the carbon emission trend and analyse it further.
# Project Structure
This is the structure that is followed for the development of the multi-agent system.
```
    parent_folder\
        |-----manager\
                |-----sub_agents\
                           |---analysis_country_agent\
                                    |---__init__.py
                                    |---.env
                                    |---agent.py
                           |---analysis_sector_agent\
                                    |---__init__.py
                                    |---.env
                                    |---agent.py
                           |---news_agent\
                                    |---__init__.py
                                    |---agent.py
                |---__init__.py
                |---.env
                |---agent.py
        |---Dockerfile
        |---main.py
        |---requirements.txt
```

# Essential Stricture Components
1. Root agent folder (here manager)
   This is the parent agent who delegates tasks to its subordinate agents.
2. Sub agents folder
   This folder holds all the subordinate agents who will be performing their assigned tasks as per user request.
3. Importing sub agents
   This is important , as this will help the manager agent to use its aub agents
   we are doing
   ``` python from .sub_agents.analysis_sector_agent.agent import analysis_sector_agent
       from .sub_agents.analysis_country_agent.agent import analysis_country_agent
       from .sub_agents.news_analyst.agent import news_analyst
   ```


# Multi - agent architecture
Using two different models
1. Sub - agents delegtion model
   
  ```  python
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
   ```


2. Agent-as-a-tool model
   
  ``` python
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
   ```

# Characteristic
a. Sub-agent returns results to the root agent
b. Root agent maintains control and can incorporate the sub-agent's response into its own.

# Emission Analysis agent tool
This multi agent system works with three specialised agents
1. analysis_country_agent : This agent helps in analysing the carbon emission data across different countries.
2. analysis_sector_agent : This agent helps in analysing the carbon emission data across different industrial sectors.
3. news_analyst : Gets the latest news from different topics and also returns insights from that.

# Cloud deployment
This multi agent system is deployed in cloud using Google's Cloud run service,and it is available for public use.
# Architecture Diagram

```
┌─────────────────────────┐
│       User Query        │
└────────────┬────────────┘
             	 ▼
┌─────────────────────────┐
│    Manager Agent (API)  │  ⇨ Parses query intent
└────────────┬────────────┘
     ┌───────▼───────────┐
     │ Delegates Task To │
     └───────┬───────────┘
               ▼
 ┌────────────────────────┬───────────────────────|
 │                        		 │                        		│
 ▼                        	 ▼                        	▼
Sector Agent           Country Agent           		News Analyst Agent
(fetch by sector)   (fetch by country)      		(semantic search on news)

   │                        │                        			│
   ▼                        ▼                        		▼
┌────────────────────────────────────────────────────────────┐
│                  MongoDB Atlas + Vector Index              │
│   Stores CO₂ emissions + news embeddings for fast queries  │
└────────────────────────────────────────────────────────────┘
	     |
             ▼
    ┌────────────────────┐
    │  Embedding Model   │  ⇨ Generates semantic vectors
    └────────────────────┘
	     |
             ▼
   ┌──────────────────────┐
   │  Insights Generator  │  ⇨ Creates trends, graphs, reports
   └────────┬─────────────┘
              ▼
  ┌────────────────────────────┐
  │   Visualization Output     │  ⇨ (Planned: Image is saved in binary format and then stored in Google storage for viewing it in the chat)
  └────────────────────────────┘
	    |
            ▼
  ┌────────────────────────────┐
  │    Google Cloud Run        │  ⇨ Hosts the entire pipeline
  └────────────────────────────┘


```



   

