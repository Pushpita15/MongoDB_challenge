from google.adk.agents import Agent
from google.cloud import storage
import uuid
import pymongo
import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
import io
from dotenv import load_dotenv
load_dotenv()
import os


MONGO_URI = os.environ.get("MONGO_URI")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME")

def get_mongo_client():
    return pymongo.MongoClient(MONGO_URI)

# These are helper functions to generate embeddings and find the closest sector name using fuzzy matchingdocker
model = SentenceTransformer('all-MiniLM-L6-v2')
def generate_embeddings(query:str) -> list:
    embeddings = model.encode(query).tolist()
    return embeddings



# This function will return an introduction to the dataset
def introduction_to_data() -> str:
    return {"result":"""This dataset contains CO2 emissions data for various sectors and subsectors. 
    It includes monthly and yearly totals, as well as percentage changes in emissions. 
    The data is structured with the following columns:
    - Sector_name: Name of the sector
    - Subsector_Name: Name of the subsector
    - Mar_2025_Total: Total CO2 emissions for March 2025
    - Prev_Month: CO2 emissions for the previous month
    - Mar_2024_Total: Total CO2 emissions for March 2024
    - Monthly_%_change: Percentage change in emissions from the previous month
    - 2025_YTD: Year-to-date total for 2025
    - 2024_YTD: Year-to-date total for 2024
    - 2023_YTD: Year-to-date total for 2023
    - 2022_YTD: Year-to-date total for 2022
    - 2021_YTD: Year-to-date total for 2021"""}
    
# This function will return a list of sectors available in the dataset
def get_sector_list() -> str:
    client = get_mongo_client()
    sectors = client['CO2_Emission_data']['Emission_data_feb'].distinct('Sector_name')
    sector_list = ["Here is the list of sectors available in the dataset:\n"]
    for sector in sectors:
        sector_list.append(sector+ "\n")
    return {"result": "\n".join(sector_list)}
# This function will return similar sectors based on the query provided by the user
def find_similar_sectors(query:str)-> str:

    client = get_mongo_client()
    query_embedding = generate_embeddings(query)
    result = client['CO2_Emission_data']['Emission_data_feb'].aggregate([
        {
            "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 6
        }
        },
        {
            '$project': {
                '_id': 0,
                'Sector_name': 1,
                'Subsector_Name': 1,
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
    result_str = ["These are the sectors that are similar to your query: \n"]
    for doc in result:
        result_str.append(f"Sector: {doc['Sector_name']}, Subsector: {doc['Subsector_Name']}, Mar_2025_Total: {doc['Mar_2025_Total']}, Monthly_%_change: {doc['Monthly_%_change']}, 2025_YTD: {doc['2025_YTD']}, 2024_YTD: {doc['2024_YTD']}, 2023_YTD: {doc['2023_YTD']}, 2022_YTD: {doc['2022_YTD']}, 2021_YTD: {doc['2021_YTD']}")
    
    return {"result_str": result_str}


# This function will generate a report for a specific sector    
def get_sector_report(sector_name:str) -> str:
    
    client = get_mongo_client()
    
    
    query_embedding = generate_embeddings(sector_name)
    sector_data = client['CO2_Emission_data']['Emission_data_feb'].aggregate([
        {
            "$vectorSearch":{
                "index":"vector_index",
                "path" : "embedding",
                "queryVector":query_embedding,
                "numCandidates":100,
                "limit": 20
                
            }
        },
        {
            "$project":{
                "_id":0,
                'Sector_name': 1,
                'Subsector_Name': 1,
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
    sector_data = pd.DataFrame(list(sector_data))
    sector_data = sector_data[sector_data['Sector_name'].astype(str).str.lower() == sector_name.lower()]
    if sector_data.empty:
        return f"No data found for sector: {sector_name}"
    else: 
        sector_summary = sector_data.groupby('Subsector_Name').agg({
            'Mar_2025_Total': 'sum',
            'Prev_Month': 'sum',
            'Mar_2024_Total': 'sum',
            "Monthly_%_change": 'mean',
            "2025_YTD": 'sum',
            "2024_YTD": 'sum',
            "2023_YTD": 'sum',
            "2022_YTD": 'sum',
            "2021_YTD": 'sum'
        }).reset_index()
        
    sector_summary_str=["Sector Report:\n"]
    for index, row in sector_summary.iterrows():
        sector_summary_str.append(
            
                f"Subsector: {row['Subsector_Name']}, Mar_2025_Total: {str(row['Mar_2025_Total'])}, Prev_Month: {str(row['Prev_Month'])}, Mar_2024_Total: {str(row['Mar_2024_Total'])}, Monthly_%_change: {str(row['Monthly_%_change'])}, 2025_YTD: {str(row['2025_YTD'])}, 2024_YTD: {str(row['2024_YTD'])}, 2023_YTD: {str(row['2023_YTD'])}, 2022_YTD: {str(row['2022_YTD'])}, 2021_YTD: {str(row['2021_YTD'])}\n"
            
        )
    return {"result" : "\n".join(sector_summary_str)}

# this function will compare two sectors based on several characteristics and return the data for both sectors
def compare_sectors(sector1:str, sector2:str) -> str:
    client = get_mongo_client()
    query_embedding1 = generate_embeddings(sector1)
    query_embedding2 = generate_embeddings(sector2)
    sector1_data = client['CO2_Emission_data']['Emission_data_feb'].aggregate([
        {
            "$vectorSearch":{
                "index":"vector_index",
                "path" : "embedding",
                "queryVector":query_embedding1,
                "numCandidates":100,
                "limit": 20
                
            }
        },
        {
            "$project":{
                "_id":0,
                'Subsector_Name': 1,
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
    sector2_data = client['CO2_Emission_data']['Emission_data_feb'].aggregate([
        {
            "$vectorSearch":{
                "index":"vector_index",
                "path" : "embedding",
                "queryVector":query_embedding2,
                "numCandidates":100,
                "limit": 100
                
            }
        },
        {
            "$project":{
                "_id":0,
                'Subsector_Name': 1,
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
    if sector1_data is None or sector2_data is None:
        return {'error': 'One or both sectors not found. Please check the sector names.'}
    else:
        sector1_data = pd.DataFrame(list(sector1_data))
        sector2_data = pd.DataFrame(list(sector2_data))
        comparison_str = ["Comparison between sectors:\n"]
        comparison_df = pd.merge(sector1_data, sector2_data, on='Subsector_Name', suffixes=('_sector1', '_sector2'))
        for index, row in comparison_df.iterrows():
            comparison_str.append(f"Subsector: {row['Subsector_Name']}, Sector1 - Mar_2025_Total: {str(row['Mar_2025_Total_sector1'])}, Sector2 - Mar_2025_Total: {str(row['Mar_2025_Total_sector2'])}, Sector1 - Monthly_%_change: {str(row['Monthly_%_change_sector1'])}, Sector2 - Monthly_%_change: {str(row['Monthly_%_change_sector2'])}")
        
    return {"result" : "\n".join(comparison_str)}



try:
    storage_client = storage.Client()
except Exception as e:
    print(f"Error initializing Google Cloud Storage client: {e}")
    storage_client = None
    
# --- Helper function to upload image to GCS ---
def _upload_to_gcs(image_data: bytes, filename: str) -> str:
    """Uploads image data to Google Cloud Storage and returns the public URL."""
    if storage_client is None:
        raise RuntimeError("Google Cloud Storage client not initialized.")

    try:
        bucket = storage_client.bucket(GCS_BUCKET)
        blob = bucket.blob(f"co2_emissions_trends/{filename}") # Path within your bucket

        # Upload from BytesIO directly
        blob.upload_from_file(io.BytesIO(image_data), content_type="image/png")
        blob.make_public() # Make public for easy viewing.
                           # For production, consider signed URLs for better security.

        return blob.public_url
    except Exception as e:
        raise RuntimeError(f"Failed to upload image to GCS: {e}")
# This function will generate a graph as a report for a specific sector
def get_graph_report(sector_name:str, parameter:str )-> str:
    client = get_mongo_client()
    
   
    query_embedding = generate_embeddings(sector_name)
    sector_data = client['CO2_Emission_data']['Emission_data_feb'].aggregate([
        {
            "$vectorSearch":{
                "index":"vector_index",
                "path" : "embedding",
                "queryVector":query_embedding,
                "numCandidates":100,
                "limit": 20
                
            }
        },
        {
            "$project":{
                "_id":0,
                'Sector_name': 1,
                'Subsector_Name': 1,
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
    sector_data = pd.DataFrame(list(sector_data))
    sector_data = sector_data[sector_data['Sector_name'].astype(str).str.lower() == sector_name.lower()]
    if sector_data.empty:
        return f"No data found for sector: {sector_name}"
    else:
        plt.figure(figsize=(20, 6))
        plt.title(f"CO2 Emissions for {sector_name} Sector")
        plt.plot(range(len(sector_data[parameter])), sector_data[parameter])
        plt.xticks(ticks=range(len(sector_data['Subsector_Name'])),
                    labels=sector_data['Subsector_Name'],
                    rotation=45,
                    ha='right')
        plt.xlabel('Subsector')
        plt.ylabel('CO2 Emissions')
        
        buf = io.BytesIO()
        plt.savefig(buf,format='png')
        buf.seek(0)
        plt.close()
        
        unique_filename = f"{sector_name.replace(' ', '_').lower()}_emissions_trend_{uuid.uuid4().hex}.png"
        try:
            image_url = _upload_to_gcs(buf.getvalue(), unique_filename)
            markdown_response = f"Here is the emissions trend for {sector_name}:\n\n![CO2 Emissions Trend for {sector_name}]({image_url})"
            return markdown_response # Return just the markdown string
        except RuntimeError as e:
            return f"Error generating or uploading image for {sector_name}: {e}"
        








    


    




analysis_sector_agent = Agent(
    name="CO2_Emission_analysis_sector_agent",
    model="gemini-2.0-flash",
    description="Agent to analyze CO2 emissions data.",
    instruction = """Start the Conversation with the user being a positive and friendly agent. Introduce yourself as the "CO2 Emission Analysis Agent" and ask user what task they would like to perform. You are a analyst agent for a climate control organization and you are here to help the user with their analysis needs.
    Additional inrtuctions:
    1. Ask for details only if you don't understand the query and are not able to search.
    2. You can use multiple tools in parallel by calling functions in parallel.
    3. If the user asks for a report for a specific sector, you can use the get_sector_report function and show the report.
    4. If the user asks for a comparison between two sectors, you can use the compare_sectors function and show the comparison mentioning the values.
    5. If the user asks for a graph report, you can use the get_graph_report function and show the graph.
    6. If the user asks for similar sectors, you can use the find_similar_sectors function and show the similar sectors.
    7. If the user asks for an introduction to the data, you can use the introduction_to_data function and show the introduction.
    8. If the user asks for a list of sectors, you can use the get_sector_list function and show the list of sectors.""",
    tools=[introduction_to_data,find_similar_sectors,compare_sectors,get_sector_report,get_graph_report,get_sector_list]
)









