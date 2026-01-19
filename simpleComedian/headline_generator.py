"""
Module for generating jokes based on news headlines.
"""
from api import generate_content

def generate_headline_joke(headline: str, language: str = 'en') -> str:
    """
    Generates a joke related to the given news headline.
    
    Args:
        headline (str): The news headline.
        language (str): The language code ('en', 'es', 'zh').
        
    Returns:
        str: The generated joke.
    """
    lang_map = {
        'en': 'English',
        'es': 'Spanish',
        'zh': 'Chinese'
    }
    
    max_length_map = {
        'en': 900,
        'es': 900,
        'zh': 300
    }
    
    full_lang = lang_map.get(language, 'English')
    max_len = max_length_map.get(language, 900)
    
    if language == 'zh':
        prompt = f"请根据以下新闻标题创作一个幽默笑话：【{headline}】。笑话必须简短有力。请仅输出中文笑话内容，不要提供选项，不要包含任何介绍性文字。例如：标题：'男子咬狗'，笑话：'看来热狗开始反击了。'"
    elif language == 'es':
        prompt = f"Escribe un chiste corto y contundente relacionado con el titular de la noticia: '{headline}'. El chiste debe estar en Español. Salida SOLAMENTE el chiste. No des opciones. No incluyas ningún texto introductorio. Ejemplo: Titular: 'Hombre muerde perro', Chiste: 'Supongo que los perritos calientes se están defendiendo.'"
    else:
        prompt = f"Write a short joke related to the news headline: '{headline}'. The joke must be in English. The joke should be short and punchy. Do not give options. Do not include any introductory text. Return ONLY the joke text. Example: Headline: 'Man bites dog', Joke: 'I guess the hot dogs are fighting back.'"
    
    # Logic retries for constraint satisfaction
    logic_retries = 3
    last_joke = None
    for attempt in range(logic_retries):
        response_text = generate_content(prompt)
        
        if response_text:
            # Normalize whitespace to remove newlines and extra spaces
            joke = " ".join(response_text.strip().split())
            last_joke = joke
            
            # Check length constraint
            if len(joke) > max_len:
                print(f"Generated joke too long ({len(joke)} > {max_len}). Retrying...")
                prompt += f" The joke must be shorter than {max_len} characters."
                continue

            # Basic check: Joke shouldn't be identical to the headline
            if joke.lower() != headline.lower():
                return joke
            else:
                print(f"Generated text identical to headline. Retrying...")
        else:
            # API failed even after its own retries
            return "Error: Could not generate joke (API failure)."
            
    if last_joke:
        print("Failed to meet length constraint after retries. Returning clipped joke.")
        return last_joke[:max_len]

    return "Error: Could not generate joke."

if __name__ == "__main__":
    # Test
    print(generate_headline_joke("Ryanair to cut 1 million more passenger seats in Spain"))
