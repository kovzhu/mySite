"""
Script to import photos for all collections from Douban album to the website.
"""

import os
import shutil
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mySite.app import app, db, ExercisePhoto, ReadingQuotePhoto, IntellectualPhoto, FragmentedQuotePhoto

BASE_SOURCE_DIR = "/Users/k/Library/Mobile Documents/com~apple~CloudDocs/08_Python/Working projects/douban/douban_album"
BASE_DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mySite/static")

def import_collection(source_subdirs, dest_subdir, ModelClass, collection_name):
    print(f"\n--- Importing {collection_name} ---")
    
    dest_dir = os.path.join(BASE_DEST_DIR, dest_subdir)
    os.makedirs(dest_dir, exist_ok=True)
    
    total_imported = 0
    
    with app.app_context():
        for subdir in source_subdirs:
            source_dir = os.path.join(BASE_SOURCE_DIR, subdir)
            if not os.path.exists(source_dir):
                print(f"Warning: Source directory not found: {source_dir}")
                continue
                
            print(f"Scanning {source_dir}...")
            files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
            print(f"Found {len(files)} images in {subdir}.")
            
            count = 0
            for filename in files:
                # Check if already exists in DB
                if ModelClass.query.filter_by(filename=filename).first():
                    # print(f"Skipping {filename} (already in DB)")
                    continue
                    
                # Copy file
                src_path = os.path.join(source_dir, filename)
                dest_path = os.path.join(dest_dir, filename)
                
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception as e:
                    print(f"Error copying {filename}: {e}")
                    continue
                
                # Create DB entry
                title = os.path.splitext(filename)[0]
                
                photo = ModelClass(
                    title=title,
                    filename=filename,
                    description=f"Imported from {subdir}",
                    created_at=datetime.utcnow()
                )
                
                db.session.add(photo)
                count += 1
                total_imported += 1
                
                if total_imported % 50 == 0:
                    db.session.commit()
                    print(f"Imported {total_imported} photos so far...")
            
            print(f"Processed {subdir}: {count} new photos.")
        
        db.session.commit()
        print(f"Successfully finished importing {collection_name}. Total new: {total_imported}")

def main():
    # Exercises
    import_collection(
        ["Exercises"], 
        "exercise_photos", 
        ExercisePhoto, 
        "Exercises"
    )
    
    # Reading Quotes
    import_collection(
        ["Reading Quotes"], 
        "reading_quote_photos", 
        ReadingQuotePhoto, 
        "Reading Quotes"
    )
    
    # Intellectual Masturbation
    import_collection(
        ["Intellectual Masturbation"], 
        "intellectual_photos", 
        IntellectualPhoto, 
        "Intellectual Masturbation"
    )
    
    # Fragmented Quotes (from Quotes and Quotes v2)
    import_collection(
        ["Quotes", "Quotes v2"], 
        "fragmented_quote_photos", 
        FragmentedQuotePhoto, 
        "Fragmented Quotes"
    )

if __name__ == "__main__":
    main()
