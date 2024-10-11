import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

def download_images(url, folder):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Send a GET request to the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all img tags
    img_tags = soup.find_all('img')

    # Download each image
    for img in img_tags:
        img_url = img.get('src')
        if img_url:
            # Make the URL absolute by joining it with the base URL
            img_url = urljoin(url, img_url)

            # Get the filename from the URL
            filename = os.path.join(folder, os.path.basename(urlparse(img_url).path))

            # Download the image
            with open(filename, 'wb') as f:
                img_data = requests.get(img_url).content
                f.write(img_data)

            print(f"Downloaded: {filename}")

# Usage example
url = "https://www.geappliances.com/"  # Replace with the actual URL
download_folder = "img"
download_images(url, download_folder)