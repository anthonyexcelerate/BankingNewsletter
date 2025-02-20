import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import time
import zipfile

# Define base directories
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")
MAIN_FOLDER = os.path.join(DESKTOP_PATH, "Banking Statistics Update")
ABS_FOLDER = os.path.join(MAIN_FOLDER, "ABS Data")

# Ensure directories exist
os.makedirs(ABS_FOLDER, exist_ok=True)

# ✅ ABS Data Sources
ABS_LENDING_URL = "https://www.abs.gov.au/statistics/economy/finance/lending-indicators/latest-release#data-downloads"
ABS_CPI_MONTHLY_URL = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/monthly-consumer-price-index-indicator/latest-release"
ABS_CPI_QUARTERLY_URL = "https://www.abs.gov.au/statistics/economy/price-indexes-and-inflation/consumer-price-index-australia/latest-release"
ABS_LABOUR_FORCE_URL = "https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release#data-downloads"
ABS_RETAIL_TRADE_URL = "https://www.abs.gov.au/statistics/industry/retail-and-wholesale-trade/retail-trade-australia/latest-release#data-downloads"

# ✅ ABS Target Files
TARGET_ABS_FILES = {
    "Housing-Finance-Total.zip": "Housing Finance Total",
    "Housing-Finance-Owner-occupiers.zip": "Housing Finance Owner-occupiers",
    "Housing-Finance-Investors.zip": "Housing Finance Investors",
    "Business-Finance.zip": "Business Finance",
    "Housing-Finance-First-home-buyers.zip": "Housing Finance First-home buyers",
}

# ✅ ABS CPI Target Files
CPI_FILES = {
    "Time-Series-Spreadsheets.zip": "Monthly Consumer Price Index",
    "All-Time-Series-Spreadsheets.zip": "Quarterly Consumer Price Index"
}

# ✅ ABS Labour Force Target File
LABOUR_FORCE_FILE_PREFIX = "6202001"  # Prefix of the latest labour force XLSX file

# ✅ ABS Retail Trade Target File
RETAIL_TRADE_FILE = "All-Time-Series-Spreadsheets.zip"  # The ZIP file name for Retail Trade data

# ------------------------------
# Helper Functions
# ------------------------------
def fetch_url(url, retries=3, wait_time=5):
    """Fetches a webpage with retries and handles blocking."""
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
        return file_path
    else:
        print(f"❌ Failed to download: {file_url}")
        return None

def extract_zip(zip_path, extract_folder):
    """Extracts the contents of a ZIP file and saves only Excel files."""
    if not zip_path or not zipfile.is_zipfile(zip_path):
        print(f"❌ Invalid ZIP file: {zip_path}")
        return
    
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith(".xlsx") or file.endswith(".xls"):
                zip_ref.extract(file, extract_folder)
                print(f"📂 Extracted: {file} to {extract_folder}")

# ------------------------------
# ABS Lending Indicators Download
# ------------------------------
def get_abs_lending_files():
    """Fetches only the five specified ABS Lending Indicator ZIP files dynamically."""
    response = fetch_url(ABS_LENDING_URL)
    if not response:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    valid_files = {}

    for link in soup.find_all("a", href=True):
        href = link["href"]
        file_name = href.split("/")[-1].split("?")[0]
        if file_name in TARGET_ABS_FILES:
            valid_files[file_name] = href if href.startswith("http") else f"https://www.abs.gov.au{href}"

    return valid_files

# ------------------------------
# ABS CPI Monthly Download
# ------------------------------
def get_abs_cpi_monthly_file():
    """Fetches the latest Monthly CPI Time-Series ZIP file dynamically."""
    response = fetch_url(ABS_CPI_MONTHLY_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "Time-Series-Spreadsheets.zip" in href:
            return href if href.startswith("http") else f"https://www.abs.gov.au{href}"

    return None

# ------------------------------
# ABS CPI Quarterly Download
# ------------------------------
def get_abs_cpi_quarterly_file():
    """Fetches the latest Quarterly CPI Time-Series ZIP file dynamically."""
    response = fetch_url(ABS_CPI_QUARTERLY_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if "All-Time-Series-Spreadsheets.zip" in href or "Time-series-spreadsheets-all.zip" in href:
            return href if href.startswith("http") else f"https://www.abs.gov.au{href}"

    return None

# ------------------------------
# ABS Labour Force Download
# ------------------------------
def get_abs_labour_force_file():
    """Fetches the latest ABS Labour Force XLSX file dynamically."""
    response = fetch_url(ABS_LABOUR_FORCE_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if LABOUR_FORCE_FILE_PREFIX in href and href.endswith(".xlsx"):
            return href if href.startswith("http") else f"https://www.abs.gov.au{href}"

    return None

# ------------------------------
# ABS Retail Trade Download
# ------------------------------
def get_abs_retail_trade_file():
    """Fetches the latest Retail Trade ZIP file dynamically."""
    response = fetch_url(ABS_RETAIL_TRADE_URL)
    if not response:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if RETAIL_TRADE_FILE in href:
            return href if href.startswith("http") else f"https://www.abs.gov.au{href}"

    return None

# ------------------------------
# Main Script Execution
# ------------------------------
if __name__ == "__main__":
    # Download ABS Lending Indicators
    abs_lending_files = get_abs_lending_files()
    for file_url in abs_lending_files.values():
        zip_path = download_file(file_url, ABS_FOLDER)
        if zip_path:
            extract_zip(zip_path, ABS_FOLDER)

    # Download ABS Monthly CPI
    download_file(get_abs_cpi_monthly_file(), ABS_FOLDER)

    # Download ABS Quarterly CPI
    download_file(get_abs_cpi_quarterly_file(), ABS_FOLDER)

    # Download ABS Labour Force
    download_file(get_abs_labour_force_file(), ABS_FOLDER)

    # Download & Extract ABS Retail Trade Data
    retail_trade_file = get_abs_retail_trade_file()
    if retail_trade_file:
        zip_path = download_file(retail_trade_file, ABS_FOLDER)
        if zip_path:
            extract_zip(zip_path, ABS_FOLDER)
    else:
        print("❌ No ABS Retail Trade file found.")
