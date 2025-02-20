import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time

# Define base directories
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAIN_FOLDER = os.path.join(DESKTOP_PATH, "Banking Statistics Update")

# RBA folder
RBA_FOLDER = os.path.join(MAIN_FOLDER, "RBA Data")

# Ensure directories exist
os.makedirs(RBA_FOLDER, exist_ok=True)

# URLs
RBA_PAYMENTS_URL = "https://www.rba.gov.au/payments-and-infrastructure/resources/payments-data.html"
RBA_INTEREST_URL = "https://www.rba.gov.au/statistics/tables/"

# RBA Interest Rate Files (Strict Matching)
TARGET_INTEREST_FILES = {
    "f01d.xlsx": "Interest Rates and Yields – Money Market – Daily – F1",
    "f01hist.xlsx": "Interest Rates and Yields – Money Market – Monthly – F1.1",
    "f06hist.xlsx": "Housing Lending Rates – F6"
}

# ------------------------------
# Helper Functions
# ------------------------------
def is_blocked(response):
    """Checks if the website has blocked access."""
    return (response.status_code in [403, 429, 503]) or ("captcha" in response.text.lower())

def fetch_url(url, retries=3, wait_time=5):
    """Fetches a webpage with retries and handles blocking."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if is_blocked(response):
                print(f"Blocked on attempt {attempt + 1}. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            else:
                return response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(wait_time)
    
    print(f"Failed to fetch {url} after {retries} attempts.")
    return None

def download_file(file_url, save_folder):
    """Downloads the file and saves it inside the specified folder with the exact filename."""
    file_name = urllib.parse.unquote(file_url.split("/")[-1].split("?")[0])  # Remove query parameters
    file_path = os.path.join(save_folder, file_name)

    print(f"\n🔗 Downloading: {file_name}")
    print(f"🌍 URL: {file_url}")

    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"✅ Saved to: {file_path}")
    else:
        print(f"❌ Failed to download: {file_url}")

# ------------------------------
# RBA Payments Data Download (Excludes Discontinued)
# ------------------------------
def get_rba_payments_files():
    """Fetches valid RBA payments data links, excluding discontinued files."""
    response = fetch_url(RBA_PAYMENTS_URL)
    if not response:
        print("Failed to fetch the RBA payments page")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    valid_files = []

    # Find and exclude discontinued section
    discontinued_section = soup.find("p", string=lambda text: text and "Discontinued payments statistical tables" in text)
    links = soup.find_all("a", href=True)

    for link in links:
        href = link["href"]

        # Stop processing at discontinued section
        if discontinued_section and link.find_parent() and discontinued_section in link.find_parents():
            print("Reached discontinued section. Stopping downloads.")
            break

        # Skip discontinued files with "xls-disc/" in URL
        if "/xls-disc/" in href:
            print(f"Skipping discontinued file: {href}")
            continue

        # Only include valid Excel files
        if href.endswith(".xls") or href.endswith(".xlsx"):
            file_url = href if href.startswith("http") else f"https://www.rba.gov.au{href}"
            valid_files.append(file_url)

    return valid_files

# ------------------------------
# RBA Interest Rates Download (Only 3 Specific Files)
# ------------------------------
def get_rba_interest_files():
    """Fetches only the three specific RBA interest rate files dynamically."""
    response = fetch_url(RBA_INTEREST_URL)
    if not response:
        print("Failed to fetch the RBA statistics page")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    
    valid_files = {}

    for link in links:
        href = link["href"]
        file_name = href.split("/")[-1].split("?")[0]  # Extract filename without query params

        if file_name in TARGET_INTEREST_FILES:
            file_url = href if href.startswith("http") else f"https://www.rba.gov.au{href}"
            valid_files[file_name] = file_url
            print(f"✅ Found latest version: {file_name} -> {file_url}")

    return valid_files

# ------------------------------
# Main Script Execution
# ------------------------------
if __name__ == "__main__":
    # 1. Download RBA Payments files (only from the correct section, excluding discontinued)
    rba_payments_files = get_rba_payments_files()
    if rba_payments_files:
        for file_url in rba_payments_files:
            print(f"🔗 Downloading RBA Payments file: {file_url}")
            download_file(file_url, RBA_FOLDER)
    else:
        print("❌ No valid RBA Payments files found")

    # 2. Download RBA Interest Rate files (only the 3 specified)
    rba_interest_files = get_rba_interest_files()
    if rba_interest_files:
        for file_name, file_url in rba_interest_files.items():
            print(f"🔗 Downloading RBA Interest Rate file: {file_name}")
            download_file(file_url, RBA_FOLDER)
    else:
        print("❌ No valid RBA Interest Rate files found")
