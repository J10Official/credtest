"""
Main script to run the joke generation pipeline.
"""
import os
from task_a_parser import parse_and_process
from task_b_parser import parse_and_process_b

DATA_DIR = "data"
OUTPUT_DIR = "output"

def main():
    # Task A
    files_to_process_a = [
        "task-a-en.tsv",
        "task-a-es.tsv",
        "task-a-zh.tsv"
    ]
    
    for filename in files_to_process_a:
        input_path = os.path.join(DATA_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(input_path):
            # Running with a limit of 10 for verification purposes. 
            # Change 'limit=10' to 'limit=None' to process the full file.
            parse_and_process(input_path, output_path, limit=0)
        else:
            print(f"Input file not found: {input_path}")

    # Task B
    files_to_process_b = [
        ("task-b1.tsv", "b1"),
        ("task-b2.tsv", "b2")
    ]

    for filename, task_type in files_to_process_b:
        input_path = os.path.join(DATA_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(input_path):
             parse_and_process_b(input_path, output_path, task_type, limit=None)
        else:
            print(f"Input file not found: {input_path}")

if __name__ == "__main__":
    main()
