from google.adk.agents import Agent
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()
import os
import base64

MONGO_URI = os.environ.get("MONGO_URI")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_mongo_client():
    return pymongo.MongoClient(MONGO_URI)

# These are helper functions to generate embeddings and find the closest sector name using fuzzy matchingdocker
model = SentenceTransformer('all-MiniLM-L6-v2')
def generate_embeddings(query:str) -> list:
    embeddings = model.encode(query).tolist()
    return embeddings

# This function will return an introduction to the dataset
def introduction_to_data() -> str:
    return {"result":"""This dataset contains CO2 emissions data for various continents and their respenctive
    countries. 
    It includes monthly and yearly totals, as well as percentage changes in emissions. 
    The data is structured with the following columns:
    - Continent: Name of the continent
    - Country: Name of the country
    - Mar_2025_Total: Total CO2 emissions for March 2025
    - Prev_Month: CO2 emissions for the previous month
    - Mar_2024_Total: Total CO2 emissions for March 2024
    - Monthly_%_change: Percentage change in emissions from the previous month
    - 2025_YTD: Year-to-date total for 2025
    - 2024_YTD: Year-to-date total for 2024
    - 2023_YTD: Year-to-date total for 2023
    - 2022_YTD: Year-to-date total for 2022
    - 2021_YTD: Year-to-date total for 2021"""}
    
# # This function will return similar sectors based on the query provided by the user
def find_similar_countries(query:str)-> str:

    client = get_mongo_client()
    query_embedding = generate_embeddings(query)
    result = client['CO2_Emission_data']['Emission_data_feb_country'].aggregate([
            {
                "$vectorSearch": {
                "index": "vector_index_country",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 10,
                "limit": 1
            }
            },
            {
                '$project': {
                    '_id': 0,
                    'Continent': 1,
                    'Country': 1,
                    'Mar_2025_Total': 1,
                    'Prev_Month':1,
                    'Mar_2024_Total':1,
                    "Monthly_%_change":1,
                    "2025_YTD":1,
                    "2024_YTD":1,
                    "2023_YTD":1,
                    "2022_YTD":1,
                    "2021_YTD":1
                    
                }
            }
        ])
    result_str = ["The data of the country: \n"]
    for doc in result:
        result_str.append(f"Continent: {doc['Continent']}, Country: {doc['Country']}, Mar_2025_Total: {doc['Mar_2025_Total']}, Monthly_%_change: {doc['Monthly_%_change']}, 2025_YTD: {doc['2025_YTD']}, 2024_YTD: {doc['2024_YTD']}, 2023_YTD: {doc['2023_YTD']}, 2022_YTD: {doc['2022_YTD']}, 2021_YTD: {doc['2021_YTD']}\n")
    return {"result_str": result_str}


def get_country_report(country: str) -> str:
    client = get_mongo_client()

    query_embedding = generate_embeddings(country)
    result = client['CO2_Emission_data']['Emission_data_feb_country'].aggregate([
            {
                "$vectorSearch": {
                "index": "vector_index_country",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 1,
                "limit": 1
            }
            },
            {
                '$project': {
                    '_id': 0,
                    'Continent': 1,
                    'Country': 1,
                    'Mar_2025_Total': 1,
                    'Prev_Month':1,
                    'Mar_2024_Total': 1,
                    "Monthly_%_change": 1,
                    "2025_YTD": 1,
                    "2024_YTD": 1,
                    "2023_YTD": 1,
                    "2022_YTD": 1,
                    "2021_YTD": 1
                }

            }
        ])
    country_data = pd.DataFrame(list(result))
    country_report_str = ["Country Report:\n"]
    country_report_str.append(f"Continent: {country_data.iloc[0]['Continent']} , Country: {country_data.iloc[0]['Country']}, Mar_2025_Total: {country_data.iloc[0]['Mar_2025_Total']}, Monthly_%_change: {country_data.iloc[0]['Monthly_%_change']}, 2025_YTD: {country_data.iloc[0]['2025_YTD']}, 2024_YTD: {country_data.iloc[0]['2024_YTD']}, 2023_YTD: {country_data.iloc[0]['2023_YTD']}, 2022_YTD: {country_data.iloc[0]['2022_YTD']}, 2021_YTD: {country_data.iloc[0]['2021_YTD']}\n")
    return {"result": country_report_str}
    

def plot_emissions_trend(country: str) -> str:
    client = get_mongo_client()
    query_embedding = generate_embeddings(country)
    result = client['CO2_Emission_data']['Emission_data_feb_country'].aggregate([
            {
                "$vectorSearch": {
                "index": "vector_index_country",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 1,
                "limit": 1
            }
            },
            {
                '$project': {
                    '_id': 0,
                    'Country': 1,
                    '2025_YTD': 1,
                    '2024_YTD': 1,
                    '2023_YTD': 1,
                    '2022_YTD': 1,
                    '2021_YTD': 1
                }
            }
        ])
    country_data = pd.DataFrame(list(result))
    print(country_data)
    if country_data.empty:
        return {"error": "No data found for the specified country."}
    else: 
        plt.figure(figsize=(20,6))
        plt.plot(range(len(country_data.iloc[0, 1:])), country_data.iloc[0, 1:])
        plt.xticks(
            ticks = range(len(country_data.iloc[0, 1:])),
            labels = country_data.columns[1:],
            rotation = 45,
            ha = 'right'
        )
        plt.title(f"CO2 Emissions Trend for {country_data.iloc[0]['Country']}")
        plt.xlabel('Year')
        plt.ylabel('CO2 Emissions')

        plt.savefig(f"{country_data.iloc[0]['Country']}_emissions_trend.png")
        plt.show()
        image_path = f"{country_data.iloc[0]['Country']}_emissions_trend.png"
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        image_data_url = base64.b64encode(image_data).decode("utf-8")
        plt.close()

    return f"Graph for {country_data.iloc[0]['Country']} saved. [View Graph]({image_data_url})"

        
        
root_agent = Agent(
    name="CO2_Emission_analysis_agent",
    model="gemini-2.0-flash",
    description="Agent to analyze CO2 emissions data.",
    instruction = """Start the Conversation with the user being a positive and friendly agent. Introduce yourself as the "CO2 Emission Analysis Agent" and ask user what task they would like to perform. You are a analyst agent for a climate control organization and you are here to help the user with their analysis needs.
    Additional inrtuctions:
    1. Ask for details only if you don't understand the query and are not able to search.
    2. You can use multiple tools in parallel by calling functions in parallel.
    3. If the user asks for similar country, you can use the find_similar_countries function and show the similar countries.
    4. If the user asks for a graph report, you can use the plot_emissions_trend function and show the graph.
    """,
    tools=[introduction_to_data,find_similar_countries, plot_emissions_trend]
)

        
