"""
Script to fix newlines in existing output TSV files.

Reads all TSV files in outputs/ directory and re-saves them with sanitized text.
"""

import csv
from pathlib import Path
from data_loader import sanitize_text_for_tsv

def fix_tsv_file(file_path: Path) -> tuple[int, int]:
    """
    Fix newlines in a TSV file.
    
    Returns:
        Tuple of (total_rows, rows_with_newlines_fixed)
    """
    if not file_path.exists():
        return (0, 0)
    
    # Read all data
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            rows.append(row)
    
    # Count and fix issues
    fixed_count = 0
    for row in rows:
        original_text = row['text']
        sanitized_text = sanitize_text_for_tsv(original_text)
        
        if original_text != sanitized_text:
            fixed_count += 1
            row['text'] = sanitized_text
    
    # Write back
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'text'])
        
        for row in rows:
            writer.writerow([row['id'], row['text']])
    
    return (len(rows), fixed_count)


def main():
    """Fix all TSV files in outputs/ directory."""
    outputs_dir = Path('outputs')
    
    if not outputs_dir.exists():
        print("No outputs/ directory found")
        return
    
    print("="*70)
    print("FIXING NEWLINES IN OUTPUT TSV FILES")
    print("="*70)
    print()
    
    total_files = 0
    total_fixed = 0
    
    for tsv_file in outputs_dir.glob('*.tsv'):
        total_rows, fixed_count = fix_tsv_file(tsv_file)
        
        if total_rows > 0:
            total_files += 1
            total_fixed += fixed_count
            
            status = "✅ Fixed" if fixed_count > 0 else "✓ Clean"
            print(f"{status} {tsv_file.name}: {total_rows} rows, {fixed_count} sanitized")
    
    print()
    print("="*70)
    print(f"Summary: {total_files} files processed, {total_fixed} rows sanitized")
    print("="*70)


if __name__ == "__main__":
    main()
