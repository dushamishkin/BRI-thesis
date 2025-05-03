import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/commodities.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)


DOWNLOAD_DIR = os.path.abspath("./downloads/commodities")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

chrome_opts = Options()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_opts.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_opts)

# Base URL
base_url = "https://tsite.shfe.com.cn/eng/reports/statistical/weekly/"
driver.get(base_url)


driver.implicitly_wait(10)


def download_table(file_name):
    try:
        # Wait for the download button to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sqs_Contract_TXT"))
        )
        driver.find_element(By.CLASS_NAME, "sqs_Contract_TXT").click()

        time.sleep(5)

        # Rename the downloaded file
        default_file_path = os.path.join(DOWNLOAD_DIR, "data.txt")  # Default file name
        new_file_path = os.path.join(DOWNLOAD_DIR, f"{file_name}.txt")  # Rename to date
        if os.path.exists(default_file_path):
            os.rename(default_file_path, new_file_path)
            logging.info(f"File renamed to: {new_file_path}")
        else:
            logging.error(f"Default file '{default_file_path}' not found.")
    except Exception as e:
        logging.error(f"Error downloading table: {e}")


def get_date():
    try:
        # Wait for the date element to be present
        date_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[2]/div[2]/div[1]/div[1]/div[1]/div[2]")
            )
        )
        date = date_element.text.strip().replace("Date: ", "")
        logging.info(f"Date found: {date}")
        return date.replace("/", "-")  # Replace slashes with dashes for file naming
    except Exception as e:
        logging.error(f"Error retrieving date: {e}")
        return "unknown_date"


def navigate_calendar():
    try:
        # Locate the table containing rows
        table = driver.find_element(
            By.XPATH, "/html/body/div[3]/div[2]/div[1]/div[1]/div/div/div/table"
        )
        rows = table.find_elements(By.TAG_NAME, "tr")

        for i in range(len(rows)):
            try:
                # Re-fetch the table and rows to avoid stale element issues
                table = driver.find_element(
                    By.XPATH, "/html/body/div[3]/div[2]/div[1]/div[1]/div/div/div/table"
                )
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Find the specific row and click the element with class "has-data"
                row = rows[i]
                button = row.find_element(By.CLASS_NAME, "has-data")
                button.click()

                # Get the date and use it to name the downloaded file
                date = get_date()
                download_table(date)

                time.sleep(2)

            except NoSuchElementException:
                logging.warning(f"No clickable element found in row {i}. Skipping...")
            except StaleElementReferenceException:
                logging.warning(f"Stale element reference at row {i}. Retrying...")
            except Exception as e:
                logging.error(f"Error processing row {i}: {e}")

    except Exception as e:
        logging.error(f"Error navigating calendar: {e}")


def change_month():
    try:
        # Locate the dropdown menu
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[2]/div[1]/div[1]/div/div/div/div/div/select[1]")
            )
        )
        select = Select(dropdown)

        # Get the current selected month
        current_month = select.first_selected_option.text.strip()
        logging.info(f"Current month: {current_month}")

        # List of months in order
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Find the index of the current month and calculate the next month
        current_index = months.index(current_month)
        next_index = (current_index + 1) % len(months)  # Wrap around to "Jan" after "Dec"
        next_month = months[next_index]

        # Select the next month
        select.select_by_visible_text(next_month)
        logging.info(f"Changed to next month: {next_month}")

        time.sleep(2)

    except Exception as e:
        logging.error(f"Error changing month: {e}")


# Main loop to navigate through all months and download files
def main():
    try:
        for _ in range(12):  # Loop through all 12 months
            navigate_calendar()
            change_month()
    finally:
        driver.quit()


if __name__ == "__main__":
    main()