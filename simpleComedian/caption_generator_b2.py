"""
Module for completing humorous prompts based on images (Task B2).
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

def generate_caption_b2(image_url: str, prompt_text: str) -> str:
    """
    Completes a humorous prompt for the given image URL.
    
    Args:
        image_url (str): The URL of the image (GIF).
        prompt_text (str): The text prompt to complete (contains '______').
        
    Returns:
        str: The completed text (full sentence or just the completion). 
             Task description says "complete a given text prompt", usually implies returning the full text or the filling.
             Let's return the full text for coherence, or we can adjust based on specific requirements.
             "generate a humorous caption... complete a given text prompt" -> likely the full caption.
    """
    if not TEST_MODE:
        image = download_image(image_url)
        if not image:
            return "Error: Could not download image."
    else:
        image = None

    # Constructing the prompt for the model
    model_prompt = f"Complete the following sentence to make a humorous caption for the image: '{prompt_text}'. Replace '______' with funny text. Keep it short (max 20 words total). Return ONLY the full completed sentence. Do not give options. Example: Prompt: 'When you see ______', Output: 'When you see a dog driving a car.'"
    
    last_caption = None
    logic_retries = 3
    max_chars = 900

    for attempt in range(logic_retries):
        response_text = generate_content([model_prompt, image])
        
        if response_text:
            caption = " ".join(response_text.strip().split())
            last_caption = caption
            if len(caption) > max_chars:
                 print(f"Caption too long ({len(caption)} chars). Retrying...")
                 model_prompt += f" Make it shorter than {max_chars} characters."
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
    test_url = "https://media4.giphy.com/media/v1.Y2lkPWE1YTU4ZDcwZzZjcnVybzBlZTI0ZHlkbzlpZ282bGFrb2xtdGxvN25yN2J0czNoNCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/2m1WldcU1mnYximIe4/giphy.gif"
    test_prompt = "When you have a celebratory dance-off and someone suddenly breaks out the ______"
    print(generate_caption_b2(test_url, test_prompt))
