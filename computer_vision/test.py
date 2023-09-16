import requests
from bs4 import BeautifulSoup
import urllib
import os

# Make a request to the web page
url = 'https://www.google.com/search?q=srubokrety&client=ubuntu&hs=W9K&channel=fs&sxsrf=APwXEdeK9yejY4LFlHvtrdlqCCc-rDCd4g:1683534723709&source=lnms&tbm=shop&sa=X&ved=2ahUKEwjvxbHJp-X-AhXvkIsKHac5A5wQ_AUoAXoECAEQAw&biw=1694&bih=861&dpr=1.09'
response = requests.get(url)
print(response)
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the image tags and extract their source URLs
image_urls = []
for img in soup.findAll('img'):
    src = img.get('src')
    if src.startswith('http'):
        image_urls.append(src)

# Download the images
for i, url in enumerate(image_urls):
    filename = f'image_{i}.jpg'
    path = os.path.join(os.getcwd(), filename)
    urllib.request.urlretrieve(url, path)
