"""
Module for parsing Task A data and generating jokes.
"""
import pandas as pd
import os
from headline_generator import generate_headline_joke
from inclusion_generator import generate_inclusion_joke
from tqdm import tqdm

def parse_and_process(input_path: str, output_path: str, limit: int = None):
    """
    Reads the input TSV, generates jokes based on constraints, and writes to output TSV.
    
    Args:
        input_path (str): Path to the input TSV file.
        output_path (str): Path to the output TSV file.
        limit (int, optional): Limit the number of rows to process. Defaults to None.
    """
    print(f"Processing {input_path}...")
    
    # Determine language from filename
    filename = os.path.basename(input_path)
    language = 'en' # Default
    if 'task-a-es' in filename:
        language = 'es'
    elif 'task-a-zh' in filename:
        language = 'zh'
    
    print(f"Detected language: {language}")
    
    try:
        df = pd.read_csv(input_path, sep='\t')
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if limit:
        df = df.head(limit)

    results = []
    
    # Using tqdm for progress bar
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Generating Jokes"):
        joke_id = row['id']
        word1 = str(row['word1']).strip()
        word2 = str(row['word2']).strip()
        headline = str(row['headline']).strip()
        
        joke_text = ""
        
        if headline != '-' and headline != 'nan' and headline:
            # Headline task
            joke_text = generate_headline_joke(headline, language=language)
        elif word1 != '-' and word2 != '-' and word1 != 'nan' and word2 != 'nan' and word1 and word2:
            # Word inclusion task
            joke_text = generate_inclusion_joke(word1, word2, language=language)
        else:
            joke_text = "Error: No valid constraint found."
            
        results.append({'id': joke_id, 'text': joke_text})
        
    output_df = pd.DataFrame(results)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    output_df.to_csv(output_path, sep='\t', index=False)
    print(f"Saved results to {output_path}")

if __name__ == "__main__":
    # Test with a dummy file if needed, or just rely on main.py
    pass
