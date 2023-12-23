import os
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, unquote
import threading

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

def download_file(url, download_directory, progress, total_files):
    """Download a file from a URL and save it in the specified directory."""
    try:
        file_name = unquote(url.split('/')[-1])
        download_path = os.path.join(download_directory, file_name)

        with urllib.request.urlopen(url) as response, open(download_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)

        progress[0] += 1
        print_progress_bar(progress[0], total_files)

    except Exception as e:
        print(f"Error downloading {url}: {e}")

def print_progress_bar(current, total):
    """Prints a simple text-based progress bar."""
    bar_length = 50
    progress_length = int((current / total) * bar_length)
    bar = '#' * progress_length + '-' * (bar_length - progress_length)
    print(f"\rProgress: [{bar}] {current}/{total}", end='')

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

# Display available files with indices
for i, file_url in enumerate(file_urls):
    file_name = unquote(file_url.split('/')[-1])
    print(f"{i}: {file_name}")

# Ask user for input on which files to download
selected_indices = input("Enter the index numbers of the files to download (separated by spaces): ")
selected_indices = selected_indices.split()

# Convert input indices to integers
selected_indices = [int(index) for index in selected_indices if index.isdigit()]

# Filter the URLs based on selected indices
selected_file_urls = [file_urls[i] for i in selected_indices if i < len(file_urls)]

# Download selected files with progress bar
progress = [0]
total_files = len(selected_file_urls)
threads = []
for file_url in selected_file_urls:
    thread = threading.Thread(target=download_file, args=(file_url, download_directory, progress, total_files))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("\nAll selected files downloaded.")
