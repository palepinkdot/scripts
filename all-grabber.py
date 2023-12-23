import os
import urllib.request
import threading
from urllib.parse import urljoin, unquote
from html.parser import HTMLParser

# URLs of the webpages you want to scrape
urls = [
    "https://archive.org/download/WiiRomSetByGhostware/",
    "https://archive.org/download/WiiRomSetByGhostwarePart2/",
    "https://archive.org/download/WiiRomSetByGhostwarePart3/"
]

class LinkParser(HTMLParser):
    """ Parser to find links in HTML content. """
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.file_urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and attr[1].endswith('.wbfs'):
                    full_url = urljoin(self.base_url, attr[1])
                    self.file_urls.append(full_url)

def download_file(url, progress, lock):
    """Download a file from a URL and save it in the specified directory."""
    try:
        file_name = unquote(url.split('/')[-1])
        download_path = os.path.join(download_directory, file_name)

        with urllib.request.urlopen(url) as response, open(download_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)

        with lock:
            progress[0] += 1
            print_progress_bar(progress[0], len(file_urls))

    except Exception as e:
        with lock:
            print(f"Error downloading {url}: {e}")

def print_progress_bar(current, total):
    """Prints a simple text-based progress bar."""
    percent = (current / total) * 100
    bar = '#' * int(percent) + '-' * (100 - int(percent))
    print(f"\r[{bar}] {current}/{total} files downloaded", end='')

# Create a directory for the downloaded files
download_directory = "downloaded_files"
os.makedirs(download_directory, exist_ok=True)

# Collect all file URLs
file_urls = []
for url in urls:
    with urllib.request.urlopen(url) as response:
        html_content = response.read().decode('utf-8')
        parser = LinkParser(url)
        parser.feed(html_content)
        file_urls.extend(parser.file_urls)

# Function to download files in batches of 5
def download_batch(file_urls, progress, lock):
    threads = []
    for url in file_urls:
        thread = threading.Thread(target=download_file, args=(url, progress, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

# Initialize progress and lock for thread safety
progress = [0]  # Using a list to allow modification in threads
lock = threading.Lock()

# Download files in batches of 5
for i in range(0, len(file_urls), 5):
    download_batch(file_urls[i:i+5], progress, lock)

print("\nAll files downloaded.")
