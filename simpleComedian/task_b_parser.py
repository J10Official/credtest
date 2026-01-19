"""
Module for parsing Task B data and generating captions.
"""
import pandas as pd
import os
from caption_generator_b1 import generate_caption_b1
from caption_generator_b2 import generate_caption_b2
from tqdm import tqdm

def parse_and_process_b(input_path: str, output_path: str, task_type: str, limit: int = None):
    """
    Reads the input TSV, generates captions, and writes to output TSV.
    
    Args:
        input_path (str): Path to the input TSV file.
        output_path (str): Path to the output TSV file.
        task_type (str): 'b1' or 'b2'.
        limit (int, optional): Limit the number of rows to process.
    """
    print(f"Processing {input_path} for Task {task_type.upper()}...")
    
    try:
        df = pd.read_csv(input_path, sep='\t')
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        return

    if limit:
        df = df.head(limit)

    results = []
    
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc=f"Generating Captions ({task_type.upper()})"):
        img_id = row['id']
        url = row['url']
        
        caption = ""
        
        if task_type == 'b1':
            caption = generate_caption_b1(url)
        elif task_type == 'b2':
            prompt_text = row['prompt']
            caption = generate_caption_b2(url, prompt_text)
            
        results.append({'id': img_id, 'text': caption})
        
    output_df = pd.DataFrame(results)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, sep='\t', index=False)
    print(f"Saved results to {output_path}")
