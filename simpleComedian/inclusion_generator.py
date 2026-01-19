"""
Module for generating jokes including specific words.
"""
from api import generate_content

def generate_inclusion_joke(word1: str, word2: str, language: str = 'en') -> str:
    """
    Generates a joke including the two specified words.
    
    Args:
        word1 (str): The first word.
        word2 (str): The second word.
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
        prompt = f"请创作一个包含词语【{word1}】和【{word2}】的幽默笑话。笑话必须简短有力。请仅输出中文笑话内容，不要提供选项，不要包含任何介绍性文字。例如：词语：'猫'，'咖啡'，笑话：'我的猫喝了咖啡，现在它是加菲猫了。'"
    elif language == 'es':
        prompt = f"Escribe un chiste corto y contundente que incluya las palabras '{word1}' y '{word2}'. El chiste debe estar en Español. Salida SOLAMENTE el chiste. No des opciones. No incluyas ningún texto introductorio. Ejemplo: Palabras: 'gato', 'café', Chiste: 'Mi gato tomó café y ahora es un gato expreso.'"
    else:
        prompt = f"Write a short joke that includes the words '{word1}' and '{word2}'. The joke must be in English. The joke should be short and punchy. Do not give options. Do not include any introductory text. Return ONLY the joke text. Example: Words: 'cat', 'coffee', Joke: 'My cat loves coffee, now he's a meow-cchiato.'"
    
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
            
            # Manual check for constraint satisfaction
            if word1.lower() in joke.lower() and word2.lower() in joke.lower():
                return joke
            else:
                print(f"Constraint check failed for '{word1}', '{word2}'. Retrying...")
                prompt += f" Make sure to include the words '{word1}' and '{word2}'."
        else:
            return "Error: Could not generate joke (API failure)."
            
    if last_joke:
        print("Failed to meet length constraint after retries. Returning clipped joke.")
        return last_joke[:max_len]

    return f"Error: Could not generate joke containing {word1} and {word2}."

if __name__ == "__main__":
    # Test
    print(generate_inclusion_joke("spray", "chair"))
