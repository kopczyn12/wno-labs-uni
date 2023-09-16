import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

def download_images(query, num_images):
    # Define the base URL for the Google Images search
    base_url = "https://www.google.com/search?q={}&source=lnms&tbm=isch"

    # Encode the query string for use in the URL
    query_encoded = urllib.parse.quote_plus(query)

    # Build the full URL for the search
    url = base_url.format(query_encoded)

    # Set up the request headers to mimic a web browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    # Send the request to the server and get the response
    response = requests.get(url, headers=headers)
    print(response)
    # Use BeautifulSoup to parse the HTML content of the response
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the image tags in the HTML content
    img_tags = soup.find_all("img")

    # Create a new directory to store the downloaded images
    if not os.path.exists(query):
        os.makedirs(query)

    # Download the first num_images images to the directory
    for i, img_tag in enumerate(img_tags):
        if i >= num_images:
            break
        try:
            # Get the URL of the image
            img_url = img_tag["src"]

            # Download the image to the directory
            img_data = requests.get(img_url, headers=headers).content
            with open(os.path.join(query, f"{query}_{i}.jpg"), "wb") as f:
                f.write(img_data)
                print('Download succesful')
        except Exception as e:
            print(f"Error downloading image {i}: {e}")

# Usage example
query = "screwdriver"
num_images = 10
download_images(query, num_images)
