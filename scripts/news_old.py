import os
import pandas as pd
import requests
from time import sleep
from dotenv import load_dotenv
import logging

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/news_2023.log"),
        logging.StreamHandler()
    ]
)

api_key = os.getenv("MEDIASTACK_API_KEY")
base_url = "https://api.mediastack.com/v1/news"

# Function to fetch news data for a specific month
def fetch_news_data(start_date, end_date, categories, countries, limit=100):
    offset = 0
    all_results = []

    while True:
        url = f"{base_url}?access_key={api_key}&date={start_date},{end_date}&categories={categories}&countries={countries}&limit={limit}&offset={offset}"
        logging.info(f"Making request to {url}")
        response = requests.get(url)

        if not response.ok:
            logging.error(f"Error: {response.status_code}, {response.text}")
            break

        data = response.json()
        if "data" not in data or not data["data"]:
            logging.info("No more data to fetch.")
            break

        all_results.extend(data["data"])
        offset += limit

    return all_results

# Main script
if __name__ == "__main__":
    # Define parameters
    categories = "general,business,technology,health,science,entertainment"
    countries = "cn,eg,hk,ma,ng,za,tw"
    months = [
        ("2023-01-01", "2023-01-31"),
        ("2023-02-01", "2023-02-28"),
        ("2023-03-01", "2023-03-31"),
        ("2023-04-01", "2023-04-30"),
        ("2023-05-01", "2023-05-31"),
        ("2023-06-01", "2023-06-30"),
        ("2023-07-01", "2023-07-31"),
        ("2023-08-01", "2023-08-31"),
        ("2023-09-01", "2023-09-30"),
        ("2023-10-01", "2023-10-31"),
        ("2023-11-01", "2023-11-30"),
        ("2023-12-01", "2023-12-31")
        # ("2024-01-01", "2024-01-31"),
        # ("2024-02-01", "2024-02-29"),
        # ("2024-03-01", "2024-03-31"),
        # ("2024-04-01", "2024-04-30"),
        # ("2024-05-01", "2024-05-31"),
        # ("2024-06-01", "2024-06-30"),
        # ("2024-07-01", "2024-07-31"),
        # ("2024-08-01", "2024-08-31"),
        # ("2024-09-01", "2024-09-30"),
        # ("2024-10-01", "2024-10-31"),
        # ("2024-11-01", "2024-11-30"),
        # ("2024-12-01", "2024-12-31")
    ]

    # Create directories if they don't exist
    os.makedirs("./downloads/news", exist_ok=True)
    os.makedirs("./data", exist_ok=True)

    all_news = []

    for start_date, end_date in months:
        logging.info(f"Fetching news for {start_date} to {end_date}")
        news_data = fetch_news_data(start_date, end_date, categories, countries)
        all_news.extend(news_data)

        # Save temporary CSV for the current month
        month_df = pd.DataFrame(news_data)
        month_file = f"./downloads/news/news_{start_date}_{end_date}.csv"
        month_df.to_csv(month_file, index=False)
        logging.info(f"Temporary data for {start_date} to {end_date} saved to {month_file}")

    # Convert all data to a single DataFrame
    news_df = pd.DataFrame(all_news)

    # Save to final CSV
    output_file = "./data/news.csv"
    news_df.to_csv(output_file, index=False)
    logging.info(f"All news data saved to {output_file}")