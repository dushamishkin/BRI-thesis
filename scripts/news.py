import os
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/news_v2.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

# Set up Selenium WebDriver
options = Options()
options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(options=options)

# Base URL
base_url = "https://www.yicai.com/news/101916631.html"
driver.get(base_url)

# Output paths
output_csv = "downloads/news/articles.csv"
backup_csv = "downloads/news/articles_backup.csv"

# Ensure output directories exist
os.makedirs(os.path.dirname(output_csv), exist_ok=True)

# Initialize data storage
all_data = []

# Function to parse an article
def parse_article():
    try:
        # Wait for and extract the title
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/h1'))
        )
        title = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/h1').text

        # Wait for and extract the datetime
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/p[1]/em'))
        )
        datetime = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/p[1]/em').text
        if counter % 10 == 0:
            logging.info(f"Oldest date is {datetime}")

        # Wait for and extract the article text
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'multi-text'))
        )
        text = driver.find_element(By.ID, 'multi-text').text

        # Click the next article link
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/div/a[1]'))
        )
        driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[3]/div/a[1]').click()

        # Return the parsed data
        return {"title": title, "datetime": datetime, "text": text}
    except Exception as e:
        logging.error(f"Error parsing article")
        return None

# Main loop
counter = 1
try:
    while True:
        try:
            # logging.info(f"Processing article #{counter}")
            time.sleep(1)

            article_data = parse_article()
            if article_data:
                all_data.append(article_data)


                # Backup every 100 articles
                if counter % 10 == 0:
                    df = pd.DataFrame(all_data)
                    df.to_csv(backup_csv, index=False)
                    logging.info(f"Backup saved after {counter} articles.")

                    current_url = driver.current_url
                    logging.info(f"Link to the last article: {current_url}")

                counter += 1
            else:
                logging.warning("Failed to parse article. Retrying...")
                time.sleep(5)  # Additional sleep on failure
        except Exception as e:
            logging.error(f"Error in processing article")
            time.sleep(5)  # Sleep before retrying
except KeyboardInterrupt:
    logging.info("Script interrupted by user.")
    driver.quit()
finally:
    logging.info("Saving and quitting the WebDriver.")

    df = pd.DataFrame(all_data)
    df.to_csv(output_csv, index=False)

    driver.quit()