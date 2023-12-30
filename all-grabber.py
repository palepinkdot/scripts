User
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import unquote
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import colorama
from colorama import Fore
import random

# Initialize colorama for colored console output
colorama.init()

# URLs of the webpages you want to scrape
urls = [
    "https://archive.org/download/WiiRomSetByGhostware/",
    "https://archive.org/download/WiiRomSetByGhostwarePart2/",
    "https://archive.org/download/WiiRomSetByGhostwarePart3/"
]

def download_file(url, download_directory, color):
    """Download a file from a URL and save it in the specified directory."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_name = unquote(url.split('/')[-1])
        # Splitting the file name to extract game name and code
        game_name_code = file_name.rsplit('.wbfs', 1)[0]  # Remove the '.wbfs' extension
        game_name, game_code = game_name_code.rsplit(' [', 1)
        game_code = game_code.replace(']', '')  # Remove the closing bracket


        # Creating a directory for the game if it doesn't exist
        game_directory = os.path.join(download_directory, f"{game_name} [{game_code}]")
        os.makedirs(game_directory, exist_ok=True)

        # Setting the download path
        download_path = os.path.join(game_directory, f"{game_code}.wbfs")
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        print(color + f"Downloading file: {file_name}")
        print(f"From URL: {url}")
        print(f"Expected size: {total_size_in_bytes / 1024 / 1024:.2f} MB" + Fore.RESET)

        block_size = 1024  # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with open(download_path, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print(color + "ERROR, something went wrong" + Fore.RESET)

        print(color + f"Downloaded {file_name}\n" + Fore.RESET)

    except requests.HTTPError as http_err:
        print(color + f"HTTP error occurred: {http_err}" + Fore.RESET)
    except Exception as err:
        print(color + f"An error occurred: {err}" + Fore.RESET)

# Create a directory for the downloaded files
download_directory = "wqb"
os.makedirs(download_directory, exist_ok=True)

# Define a list of colors for console output
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]

# List to store file URLs
file_urls = []

# Extract file URLs from each page
for url in urls:
    response = requests.get(url)
    response.raise_for_status() 
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    for link in links:
        href = link.get('href')
        if href and href.endswith('.wbfs'):
            file_url = url + href
            file_urls.append(file_url)

# Number of threads to use for downloading
num_threads = 5

# Download files using multiple threads
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    for file_url in file_urls:
        color = random.choice(colors)  # Randomly choose a color for each download
        executor.submit(download_file, file_url, download_directory, color)

print(Fore.RESET + "All files downloaded.")