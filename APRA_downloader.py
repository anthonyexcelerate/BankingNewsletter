import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time

# Define directories
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAIN_FOLDER = os.path.join(DESKTOP_PATH, "Banking Statistics Update")
APRA_FOLDER = os.path.join(MAIN_FOLDER, "APRA Data")  # Updated folder name

# Ensure directories exist
os.makedirs(APRA_FOLDER, exist_ok=True)

# ✅ APRA Data Source
APRA_URL = "https://www.apra.gov.au/monthly-authorised-deposit-taking-institution-statistics"

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
    """Downloads and saves the file with its original name."""
    file_name = urllib.parse.unquote(file_url.split("/")[-1].split("?")[0])  # Keep original filename
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
# APRA Data Scraping
# ------------------------------
def get_apra_file():
    """Fetches the latest APRA back-series Excel file."""
    response = fetch_url(APRA_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.text.strip().lower()
        if href.endswith(".xlsx") and "back-series" in text:
            return href if href.startswith("http") else f"https://www.apra.gov.au{href}"

    return None

# ------------------------------
# Main Script Execution
# ------------------------------
if __name__ == "__main__":
    # Download APRA Back-Series File
    apra_file_url = get_apra_file()
    if apra_file_url:
        download_file(apra_file_url, APRA_FOLDER)
    else:
        print("❌ No APRA back-series file found.")
