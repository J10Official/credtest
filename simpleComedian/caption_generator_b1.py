"""
Module for generating humorous captions for images (Task B1).
"""
from api import generate_content, TEST_MODE
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

def generate_caption_b1(image_url: str) -> str:
    """
    Generates a humorous caption for the given image URL.
    
    Args:
        image_url (str): The URL of the image (GIF).
        
    Returns:
        str: The generated caption.
    """
    if not TEST_MODE:
        image = download_image(image_url)
        if not image:
            return "Error: Could not download image."
    else:
        image = None

    prompt = "Generate a humorous caption for this image. The caption should be short (max 20 words) and funny. Do not include any introductory text or options. Just the caption. Example: 'When you realize it's Monday.'"
    
    last_caption = None
    logic_retries = 3
    max_chars = 900

    for attempt in range(logic_retries):
        response_text = generate_content([prompt, image])
        
        if response_text:
            caption = " ".join(response_text.strip().split())
            last_caption = caption
            # Check character count
            if len(caption) > max_chars:
                 print(f"Caption too long ({len(caption)} chars). Retrying...")
                 prompt += f" Make it shorter than {max_chars} characters."
                 continue
            return caption
        else:
            return "Error: Could not generate caption (API failure)."
            
    if last_caption:
        print("Failed to meet length constraint after retries. Returning clipped caption.")
        return last_caption[:max_chars]

    return "Error: Could not generate caption."

if __name__ == "__main__":
    # Test
    test_url = "https://media0.giphy.com/media/v1.Y2lkPWE1YTU4ZDcwYWhoYXF0MjhzZTRtZW9lZnZvNWdwYTR0aXV6aGR0dDgyM2txaTAxaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/fR1dfCFLiXGTPhyE46/giphy.gif"
    print(generate_caption_b1(test_url))
