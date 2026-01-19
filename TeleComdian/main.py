import os
import pandas as pd
from tqdm import tqdm
from src.pipeline import TeleComedianPipeline
from src.data_loader import DataLoader
from src.utils import download_image

# Configuration
DATA_DIR = "data"
OUTPUT_DIR = "output"
LIMIT = 5 # Set to None for full run

def main():
    # Initialize pipelines for each language
    pipelines = {
        'en': TeleComedianPipeline(language='en'),
        'es': TeleComedianPipeline(language='es'),
        'zh': TeleComedianPipeline(language='zh')
    }
    
    loader = DataLoader(DATA_DIR)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Task A ---
    task_a_files = [
        "task-a-en.tsv",
        "task-a-es.tsv",
        "task-a-zh.tsv"
    ]
    
    for filename in task_a_files:
        print(f"Processing {filename}...")
        results = []
        items = list(loader.load_task_a(filename))
        
        if LIMIT:
            items = items[:LIMIT]
            
        lang_label = items[0]['language'] if items else 'unknown'
        current_pipeline = pipelines.get(lang_label, pipelines['en'])
        
        for item in tqdm(items, desc=f"Task A {lang_label}"):
            try:
                joke = current_pipeline(
                    input_item=item['input'],
                    task_type=item['type'],
                    language=item['language'],
                    constraints=item['constraints'],
                    word1=item.get('word1'),
                    word2=item.get('word2')
                )
                results.append({'id': item['id'], 'text': joke})
            except Exception as e:
                print(f"Error processing {item['id']}: {e}")
                results.append({'id': item['id'], 'text': "Error"})
        
        # Save results
        if results:
            out_df = pd.DataFrame(results)
            out_path = os.path.join(OUTPUT_DIR, filename)
            out_df.to_csv(out_path, sep='\t', index=False)
            print(f"Saved to {out_path}")

    # --- Task B ---
    task_b_files = [
        ("task-b1.tsv", "b1"),
        ("task-b2.tsv", "b2")
    ]
    
    # Task B is English only
    current_pipeline = pipelines['en']
    
    for filename, subtype in task_b_files:
        print(f"Processing {filename} ({subtype})...")
        results = []
        items = list(loader.load_task_b(filename, subtype))
        
        if LIMIT:
            items = items[:LIMIT]
            
        for item in tqdm(items, desc=f"Task B {subtype}"):
            try:
                # Download image
                image_data = download_image(item['image_url'])
                if not image_data:
                    results.append({'id': item['id'], 'text': "Error: Image download failed"})
                    continue
                
                caption = current_pipeline(
                    input_item=item['input'],
                    task_type=subtype,
                    language='en',
                    constraints=item['constraints'],
                    image_data=image_data
                )
                results.append({'id': item['id'], 'text': caption})
            except Exception as e:
                print(f"Error processing {item['id']}: {e}")
                results.append({'id': item['id'], 'text': "Error"})

        # Save results
        if results:
            out_df = pd.DataFrame(results)
            out_path = os.path.join(OUTPUT_DIR, filename)
            out_df.to_csv(out_path, sep='\t', index=False)
            print(f"Saved to {out_path}")

if __name__ == "__main__":
    main()
