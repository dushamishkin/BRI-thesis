import os
import pandas as pd
import json
import requests
from time import sleep
from dotenv import load_dotenv
import logging

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/port-calls.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

load_dotenv()
api_key = os.getenv("API_KEY")

# Configure download directory
DOWNLOAD_DIR = os.path.abspath("./downloads/port-calls")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def make_request(unloco, fromdate, todate):
    url = f"https://api.myshiptracking.com/api/v2/port/calls?unloco={unloco}&fromdate={fromdate}&todate={todate}"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    logging.info(f"Making request to {url}")
    response = requests.get(url, headers=headers)
    if not response.ok:
        logging.error(f"Error: {response.status_code}, {response.text}")

    return response.json()

def to_df(json_data):
    data = json_data.get("data", [])
    new_df = pd.DataFrame(data)

    return new_df

def get_port_data(unloco):
    combined_df = pd.DataFrame()
    
    for month in range(1, 13):
        month_str = f"{month:02d}"
        fromdate = f"2024-{month_str}-01T00:00:00Z"
        todate = f"2024-{month_str}-31T00:00:00Z"

        data = make_request(unloco, fromdate, todate)
        if data:
            new_df = to_df(data)
            combined_df = pd.concat([combined_df, new_df], ignore_index=True)
        else:
            logging.warning(f"Port {unloco}: no data for {month_str}.")
        
        sleep(1)
    
    return combined_df

ports_dict = {
    "toamasina": "MGTOA",
    "durban": "ZADUR",
    "richards_bay": "ZARCB",
    "cape_town": "ZACPT",
    "port_elizabeth": "ZAPLZ",
    "east_london": "ZAELS",
    "saldanha": "ZASDB",
    "coega": "ZAZBA",
    "walvis_bay": "NAWVB",
    "beira": "MZBEW",
    "maputo": "MZMPM",
    "djibouti": "DJJIB",
    "said": "EGPSD",
    "mombasa": "KEMBA",
    "casablanca": "MACAS",
    "lome": "TGLFW",
    "abidjan": "CIABJ",
    "tema": "GHTEM",
    "dakar": "SNDKR",
    "douala": "CMDLA",
    "gentil": "GAPOG",
    "conakry": "GNCKY",
    "pointe_noire": "CGPNR",
    "matadi": "CDMAT",
    "monrovia": "LRMLW",
    "cotonou": "BJCOO",
    "dar_es_salaam": "TZDAR",
    "berbera": "SOBBO"
}

baseline_df = pd.DataFrame()

for unloco in ports_dict.values():
    logging.info(f"PROCESSING PORT: {unloco}")
    port_data = get_port_data(unloco)
    if not port_data.empty:
        baseline_df = pd.concat([baseline_df, port_data], ignore_index=True)
        backup_path = os.path.join(DOWNLOAD_DIR, f"backup_{unloco}.csv")
        baseline_df.to_csv(backup_path, index=False)
        logging.info(f"Data for port {unloco} added to baseline DataFrame.")
        logging.info(f"Unique port ids: {baseline_df['port_name'].unique()}")
    else:
        logging.warning(f"No data for port {unloco}.")

all_ports_path = os.path.join(DOWNLOAD_DIR, "ALL_ports.csv")
baseline_df.to_csv(all_ports_path, index=False)
logging.info(f"All port data saved to {all_ports_path}")