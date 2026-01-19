import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load_task_a(self, filename):
        """
        Yields items for Task A (Headlines or Word Inclusion).
        """
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        df = pd.read_csv(path, sep='\t')
        
        # Determine language
        lang = 'en'
        if 'es' in filename: lang = 'es'
        elif 'zh' in filename: lang = 'zh'

        for _, row in df.iterrows():
            item = {
                'id': row['id'],
                'language': lang,
                'type': 'unknown',
                'input': None,
                'constraints': None
            }
            
            headline = str(row.get('headline', '-')).strip()
            word1 = str(row.get('word1', '-')).strip()
            word2 = str(row.get('word2', '-')).strip()

            if headline and headline != '-' and headline != 'nan':
                item['type'] = 'headline'
                item['input'] = headline
                item['word1'] = None
                item['word2'] = None
                # Constraints handled by pipeline logic, but we can pass explicit ones
                if lang == 'zh':
                    item['constraints'] = "Max 300 chars. Must be related to headline."
                else:
                    item['constraints'] = "Max 900 chars. Must be related to headline."
            
            elif word1 and word2 and word1 != '-' and word1 != 'nan':
                item['type'] = 'words'
                item['input'] = f"{word1}, {word2}"
                item['word1'] = word1
                item['word2'] = word2
                if lang == 'zh':
                    item['constraints'] = f"Max 300 chars. Must include {word1} and {word2}."
                else:
                    item['constraints'] = f"Max 900 chars. Must include {word1} and {word2}."
            
            if item['input']:
                yield item

    def load_task_b(self, filename, task_subtype):
        """
        Yields items for Task B (Image Captioning).
        task_subtype: 'b1' (Image only) or 'b2' (Image + Prompt)
        """
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        df = pd.read_csv(path, sep='\t')
        
        for _, row in df.iterrows():
            item = {
                'id': row['id'],
                'language': 'en', # Task B is English only
                'type': task_subtype,
                'image_url': row['url'],
                'input': None,
                'constraints': "Max 20 words. Funny caption."
            }
            
            if task_subtype == 'b2':
                item['input'] = row['prompt']
            else:
                item['input'] = "" # B1 has no text input, just image
                
            yield item
