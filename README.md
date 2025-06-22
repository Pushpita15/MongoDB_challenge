# Carbon Emission Analysis agent
This project aims to develop an agent that analyses Carbon emission data . The agent analyses the carbon emission from different industrial sectors and countries, and also it is capable of providing latest news on the carbon emission trend and analyse it further.
# Project Structure
This is the structure that is followed for the development of the multi-agent system.

![image](https://github.com/user-attachments/assets/43eab7ef-f9b6-48ff-81a7-4856b3abc176)


# Essential Stricture Components
1. Root agent folder (here manager)
   This is the parent agent who delegates tasks to its subordinate agents.
2. Sub agents folder
   This folder holds all the subordinate agents who will be performing their assigned tasks as per user request.
3. Importing sub agents
   This is important , as this will help the manager agent to use its aub agents
   we are doing
   ![image](https://github.com/user-attachments/assets/37bfa4d0-4ee8-42e2-ace6-8d9394e7c195)
   

# Multi - agent architecture
Using two different models
1. Sub - agents delegtion model
   
   ![image](https://github.com/user-attachments/assets/8f2efa18-2817-43f5-80b0-6238a832242b)


2. Agent-as-a-tool model
   
   ![image](https://github.com/user-attachments/assets/e02b793a-0b4e-478d-88a3-56fccc54151c)

# Characteristic
a. Sub-agent returns results to the root agent
b. Root agent maintains control and can incorporate the sub-agent's response into its own.

# Emission Analysis agent tool
Has these three sub agents to perform different analysus tasks



   

