import os
import pandas as pd
import requests
from time import sleep
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
secret = os.getenv("SECRET")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../logs/vessels.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

# Configure output file path
OUTPUT_FILE = os.path.abspath("../data/vessels/vessels_info.csv")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Function to convert JSON data to a DataFrame
def to_df(json_data):
    data = json_data.get("data", [])
    new_df = pd.DataFrame(data)
    return new_df

# Function to make API requests
def make_request(mmsi_list):
    url = f"https://api.myshiptracking.com/api/v2/vessel/bulk?mmsi={mmsi_list}&response=extended"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        logging.error(f"Error: {response.status_code}, {response.text}")
    return response.json()

# Load vessel data
port_calls = pd.read_csv("../data/port_calls.csv")
vessels_list = port_calls.mmsi.unique().tolist()

# Initialize an empty DataFrame
combined_df = pd.DataFrame()

# Process vessels in chunks of 100
for i in range(0, len(vessels_list), 100):
    chunk = vessels_list[i:i+100]
    mmsi_list = ",".join(map(str, chunk))

    data = make_request(mmsi_list)
    if data:
        new_df = to_df(data)
        combined_df = pd.concat([combined_df, new_df], ignore_index=True)
    else:
        logging.warning(f"Chunk {chunk}: no data")

    sleep(0.5)
    logging.info(f"Chunk {chunk}: DONE")

# Save the final combined DataFrame to a single CSV file
combined_df.to_csv(OUTPUT_FILE, index=False)
logging.info(f"Data saved to {OUTPUT_FILE}")