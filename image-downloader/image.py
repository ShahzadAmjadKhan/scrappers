import os
import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to get the image name from the URL or generate it from base64 content
def get_image_name(image_url, index=None, is_base64=False, base64_type=None, is_svg=False):
    if is_base64:
        # Generate a name for the base64-encoded image
        return f"base64_image_{index}.{base64_type.split('/')[-1]}"  # Get file extension from MIME type
    elif is_svg:
        # SVG image: no extension logic needed
        return f"svg_image_{index+1}.svg"
    else:
        # Extract the image name from the URL
        url_path = urlparse(image_url).path
        image_name = url_path.split("/")[-1]

        # If no extension is found, extract it from the `fm` query parameter
        if '.' not in image_name:
            query_params = parse_qs(urlparse(image_url).query)
            extension = query_params.get('fm', ['jpg'])[0]  # Default to 'jpg' if 'fm' is not available
            image_name += f".{extension}"

        return image_name.split("?")[0]  # Handle URLs with query parameters

# Function to download a single image
def download_image(image_url, folder_path, index=None):
    image_name = get_image_name(image_url, index=index)

    try:
        # Make a request to get the image content
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            # Save the image content to the specified folder
            with open(os.path.join(folder_path, image_name), 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {image_name}")
        else:
            print(f"Failed to download {image_name} (status code: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_name}: {e}")

# Function to save base64-encoded images
def save_base64_image(base64_data, mime_type, folder_path, index):
    # Get the correct image extension from the mime type
    image_name = get_image_name(None, index=index, is_base64=True, base64_type=mime_type)

    # Decode base64 content
    image_data = base64.b64decode(base64_data)

    # Save the image to the specified folder
    with open(os.path.join(folder_path, image_name), 'wb') as f:
        f.write(image_data)
    print(f"Saved base64 image: {image_name}")

# Function to scrape all image URLs and inline SVGs from the webpage
def get_image_data(url):
    # Make a request to get the webpage content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return [], []

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all img tags and their sources
    img_tags = soup.find_all('img')
    svg_tags = soup.find_all('svg')

    # Collect image URLs and base64 images
    img_urls = []
    base64_images = []

    for index, img_tag in enumerate(img_tags):
        img_src = img_tag.get('src') or img_tag.get('data-src')
        if img_src:
            if img_src.startswith('data:image'):  # Handle base64-encoded images
                mime_type, base64_data = img_src.split(',')[0].split(';')[0], img_src.split(',')[1]
                base64_images.append((base64_data, mime_type, index))
            else:  # Standard image URL
                img_urls.append(urljoin(url, img_src))

    # Collect inline SVGs as strings (to be saved as SVG files)
    svg_strings = [str(svg_tag) for svg_tag in svg_tags]

    return img_urls, base64_images, svg_strings

# Function to save inline SVGs to files
def save_svgs(svg_strings, folder_path):
    for i, svg_content in enumerate(svg_strings):
        svg_name = get_image_name(None, index=i, is_svg=True)
        with open(os.path.join(folder_path, svg_name), 'w') as f:
            f.write(svg_content)
        print(f"Downloaded SVG: {svg_name}")

# Function to scrape and download all images (including base64 and SVG) from a webpage
def scrape_images_from_page(url, folder_path='images'):
    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Get all image URLs, base64 images, and SVG contents
    img_urls, base64_images, svg_strings = get_image_data(url)

    # Use ThreadPoolExecutor to download regular images in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_image, img_url, folder_path, index) for index, img_url in enumerate(img_urls)]

        # Wait for all image downloads to complete
        for future in as_completed(futures):
            future.result()  # Handle any exceptions during the download process

    # Save base64-encoded images
    for base64_data, mime_type, index in base64_images:
        save_base64_image(base64_data, mime_type, folder_path, index)

    # Save inline SVGs
    save_svgs(svg_strings, folder_path)

# Example usage
if __name__ == "__main__":
    website_url = "https://unsplash.com/"  # Replace with the target URL
    scrape_images_from_page(website_url)
