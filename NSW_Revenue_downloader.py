import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time

# Define directories
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAIN_FOLDER = os.path.join(DESKTOP_PATH, "Banking Statistics Update")
NSW_REVENUE_FOLDER = os.path.join(MAIN_FOLDER, "NSW Revenue Data")

# Ensure directories exist
os.makedirs(NSW_REVENUE_FOLDER, exist_ok=True)

# ✅ NSW Revenue Data Source
NSW_REVENUE_URL = "https://www.revenue.nsw.gov.au/help-centre/resources-library/statistics"

# ✅ Target File Name
TARGET_NSW_REVENUE_FILE = "transfer-duty-land-related-dsd-001.xlsx"

# ------------------------------
# Helper Functions
# ------------------------------
def fetch_url(url, retries=3, wait_time=5):
    """Fetches a webpage with retries."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code in [403, 429, 503] or "captcha" in response.text.lower():
                print(f"🔴 Blocked on attempt {attempt + 1}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                return response
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error fetching {url}: {e}")
            time.sleep(wait_time)
    
    print(f"❌ Failed to fetch {url} after {retries} attempts.")
    return None

def download_file(file_url, save_folder):
    """Downloads and saves the file."""
    file_name = urllib.parse.unquote(file_url.split("/")[-1].split("?")[0])
    file_path = os.path.join(save_folder, file_name)

    print(f"\n🔗 Downloading: {file_name}")
    print(f"🌍 URL: {file_url}")

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"✅ Saved to: {file_path}")
        return file_path
    else:
        print(f"❌ Failed to download: {file_url}")
        return None

# ------------------------------
# NSW Revenue Data Scraping
# ------------------------------
def get_nsw_revenue_file():
    """Fetches the latest NSW Revenue Transfer Duty Excel file."""
    response = fetch_url(NSW_REVENUE_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if TARGET_NSW_REVENUE_FILE in href:
            return href if href.startswith("http") else f"https://www.revenue.nsw.gov.au{href}"

    return None

# ------------------------------
# Main Script Execution
# ------------------------------
if __name__ == "__main__":
    # Download NSW Revenue Transfer Duty Excel File
    nsw_revenue_file = get_nsw_revenue_file()
    if nsw_revenue_file:
        download_file(nsw_revenue_file, NSW_REVENUE_FOLDER)
    else:
        print("❌ No NSW Revenue Transfer Duty file found.")
