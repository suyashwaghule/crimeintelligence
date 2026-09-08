#!/usr/bin/env python3
"""
Crime Analysis System - Image Renamer
Description: Scans extracted_images/ folder, groups images by person name,
             assigns each unique person a sequential criminal ID (CRM-IND-XXXXX),
             and copies/renames them into output_dataset/mock_images/faces/ using
             the project naming convention:
               - First image  -> CRM-IND-XXXXX_mugshot.jpg
               - Remaining    -> CRM-IND-XXXXX_face_1.jpg, _face_2.jpg, ...
"""

import os
import shutil
import time
from collections import defaultdict

def main():
    # Resolve paths relative to this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))

    extracted_dir = os.path.join(base_dir, "extracted_images")
    target_faces_dir = os.path.join(base_dir, "output_dataset", "mock_images", "faces")

    print("=" * 60)
    print("  Crime Analysis System - Image Renamer")
    print("=" * 60)

    # 1. Verify source directory
    if not os.path.exists(extracted_dir):
        print(f"\n[-] Error: Source directory '{extracted_dir}' not found.")
        print("    Please run extract_images.py first to extract LFW images.")
        return

    # 2. Create target directory
    if not os.path.exists(target_faces_dir):
        os.makedirs(target_faces_dir)
        print(f"\n[+] Created target directory: {target_faces_dir}")
    else:
        print(f"\n[*] Target directory already exists: {target_faces_dir}")

    # 3. Scan extracted_images for all .jpg/.jpeg files
    print("\n[*] Scanning extracted_images/ for image files...")
    all_files = [
        f for f in os.listdir(extracted_dir)
        if f.lower().endswith(('.jpg', '.jpeg'))
    ]

    if not all_files:
        print("[-] No .jpg/.jpeg images found in extracted_images/. Nothing to do.")
        return

    print(f"[+] Found {len(all_files)} total image files.")

    # 4. Group images by person name
    #    Filename pattern: "PersonName_XXXX.jpg" (e.g. "Aaron_Peirsol_0001.jpg")
    #    We split on the LAST underscore to separate the person name from the serial number.
    print("[*] Grouping images by person name...")
    people_images = defaultdict(list)

    for filename in all_files:
        name_no_ext = os.path.splitext(filename)[0]  # e.g. "Aaron_Peirsol_0001"
        if '_' in name_no_ext:
            # Split on last underscore: "Aaron_Peirsol" + "0001"
            person_name, _ = name_no_ext.rsplit('_', 1)
            people_images[person_name].append(filename)
        else:
            # No underscore — treat entire name as person name
            people_images[name_no_ext].append(filename)

    # Sort each person's images by filename for consistent ordering
    for person in people_images:
        people_images[person].sort()

    sorted_people = sorted(people_images.keys())
    total_people = len(sorted_people)

    print(f"[+] Identified {total_people} unique people.\n")

    # 5. Assign criminal IDs and rename/copy
    print("[*] Renaming and copying images...")
    print(f"    Format: CRM-IND-XXXXX_mugshot.jpg  (first image per person)")
    print(f"    Format: CRM-IND-XXXXX_face_N.jpg   (additional images)\n")

    start_time = time.time()
    total_copied = 0
    total_mugshots = 0
    total_faces = 0

    for idx, person_name in enumerate(sorted_people, start=1):
        criminal_id = f"CRM-IND-{idx:05d}"
        images = people_images[person_name]

        for img_idx, src_filename in enumerate(images):
            src_path = os.path.join(extracted_dir, src_filename)

            if img_idx == 0:
                # First image → mugshot
                dest_name = f"{criminal_id}_mugshot.jpg"
                total_mugshots += 1
            else:
                # Subsequent images → face angles
                dest_name = f"{criminal_id}_face_{img_idx}.jpg"
                total_faces += 1

            dest_path = os.path.join(target_faces_dir, dest_name)

            try:
                shutil.copy2(src_path, dest_path)
                total_copied += 1
            except Exception as e:
                print(f"  [-] Error copying {src_filename} -> {dest_name}: {e}")

        # Progress update every 500 people or at the end
        if idx % 500 == 0 or idx == total_people:
            elapsed = time.time() - start_time
            rate = total_copied / elapsed if elapsed > 0 else 0
            pct = (idx / total_people) * 100
            print(f"    Progress: {idx}/{total_people} people ({pct:.1f}%) | "
                  f"Files copied: {total_copied} | Speed: {rate:.0f} files/sec")

    end_time = time.time()
    total_elapsed = end_time - start_time

    # 6. Summary
    print("\n" + "=" * 60)
    print("  RENAMING COMPLETE!")
    print("=" * 60)
    print(f"  Unique people mapped:     {total_people}")
    print(f"  Mugshot images created:   {total_mugshots}")
    print(f"  Face angle images created:{total_faces}")
    print(f"  Total files copied:       {total_copied}")
    print(f"  Time taken:               {total_elapsed:.2f} seconds")
    print(f"  Output directory:         {target_faces_dir}")
    print(f"\n  Criminal IDs assigned:    CRM-IND-00001  to  CRM-IND-{total_people:05d}")
    print("=" * 60)


if __name__ == "__main__":
    main()
