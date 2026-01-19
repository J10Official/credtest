import requests
from PIL import Image
from io import BytesIO

def download_image(url: str):
    """
    Downloads an image from a URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None
