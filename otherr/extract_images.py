#!/usr/bin/env python3
"""
LFW Image Extractor
Description: Recursively extracts all images from subfolders of lfw-deepfunneled
             and copies them into a new flat folder named 'extracted_images'.
"""

import os
import glob
import shutil
import time

def main():
    source_dir = "lfw-deepfunneled"
    target_dir = "extracted_images"
    
    print("[*] Initializing LFW Image Extractor...")
    
    # Verify source directory exists
    if not os.path.exists(source_dir):
        print(f"[-] Error: Source directory '{source_dir}' not found.")
        return
        
    # Create target directory
    if not os.path.exists(target_dir):
        print(f"[*] Creating target directory '{target_dir}'...")
        os.makedirs(target_dir)
    else:
        print(f"[*] Target directory '{target_dir}' already exists.")

    # Find all images recursively
    print("[*] Scanning source directory for images...")
    image_patterns = [
        os.path.join(source_dir, "**", "*.jpg"),
        os.path.join(source_dir, "**", "*.jpeg")
    ]
    
    source_files = []
    for pattern in image_patterns:
        source_files.extend(glob.glob(pattern, recursive=True))
        
    total_files = len(source_files)
    print(f"[+] Found {total_files} images to extract.")
    
    if total_files == 0:
        print("[-] No images found in source directory.")
        return

    # Start copying
    start_time = time.time()
    copied_count = 0
    
    print("[*] Starting extraction process...")
    for idx, filepath in enumerate(source_files, start=1):
        filename = os.path.basename(filepath)
        dest_path = os.path.join(target_dir, filename)
        
        try:
            shutil.copy2(filepath, dest_path)
            copied_count += 1
        except Exception as e:
            print(f"\n[-] Error copying {filepath} to {dest_path}: {e}")
            
        # Print progress update
        if idx % 1000 == 0 or idx == total_files:
            elapsed = time.time() - start_time
            rate = copied_count / elapsed if elapsed > 0 else 0
            print(f"    Progress: {idx}/{total_files} files processed ({idx/total_files*100:.1f}%) | Speed: {rate:.1f} files/sec")

    end_time = time.time()
    total_elapsed = end_time - start_time
    
    print("\n[+] Extraction complete!")
    print(f"    Total files found: {total_files}")
    print(f"    Successfully extracted: {copied_count}")
    print(f"    Time taken: {total_elapsed:.2f} seconds")
    print(f"    All images are located in the folder: '{os.path.abspath(target_dir)}'")

if __name__ == "__main__":
    main()
