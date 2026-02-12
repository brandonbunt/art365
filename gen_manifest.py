#!/usr/bin/env python3
"""
Generate manifest.json for art-365 repository
Run this in the root of your art365 repo
"""

import os
import re
import json

def parse_filename(filename):
    """
    Parse filename format: "1. The Sun by Giuseppe Pellizza da Volpedo, 1904.jpg"
    Returns: (number, title, artist, year)
    """
    # Remove extension
    name = os.path.splitext(filename)[0]
    
    # Pattern: number. title by artist, year
    match = re.match(r'(\d+)\.\s*(.+?)\s+by\s+(.+?),\s*(\d{4})', name)
    if match:
        number = int(match.group(1))
        title = match.group(2).strip()
        artist = match.group(3).strip()
        year = int(match.group(4))
        return number, title, artist, year
    
    # Fallback: try without title (just in case format varies)
    # "42. Artist Name, 1872.jpg"
    match = re.match(r'(\d+)\.\s*(.+?),\s*(\d{4})', name)
    if match:
        number = int(match.group(1))
        title = None
        artist = match.group(2).strip()
        year = int(match.group(3))
        return number, title, artist, year
    
    print(f"Warning: Could not parse filename: {filename}")
    return None, None, None, None

def generate_manifest(images_dir="images"):
    """
    Generate manifest from images directory
    """
    if not os.path.exists(images_dir):
        print(f"Error: Directory '{images_dir}' not found!")
        print("Make sure you're running this from the art365 repo root")
        return
    
    manifest = {
        "version": "1.0",
        "total_images": 0,
        "images": []
    }
    
    # Get all image files
    image_files = [f for f in os.listdir(images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Sort by number
    image_files.sort(key=lambda x: int(re.match(r'(\d+)', x).group(1)) if re.match(r'(\d+)', x) else 999)
    
    print(f"Found {len(image_files)} images in {images_dir}/")
    print("Parsing filenames...\n")
    
    for filename in image_files:
        number, title, artist, year = parse_filename(filename)
        
        if number is not None:
            entry = {
                "id": number,
                "filename": filename,
                "artist": artist,
                "year": year,
                "url": f"https://raw.githubusercontent.com/brandonbunt/art365/main/images/{filename}"
            }
            
            if title:
                entry["title"] = title
            
            manifest["images"].append(entry)
            
            # Print progress
            if title:
                print(f"✓ {number:3d}. {title} by {artist}, {year}")
            else:
                print(f"✓ {number:3d}. {artist}, {year}")
    
    manifest["total_images"] = len(manifest["images"])
    
    # Write manifest
    output_file = "manifest.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Generated {output_file}")
    print(f"  Total images: {manifest['total_images']}")
    print(f"\nNext steps:")
    print(f"  git add manifest.json")
    print(f"  git commit -m 'Add manifest.json for art metadata'")
    print(f"  git push origin main")

if __name__ == "__main__":
    generate_manifest()
