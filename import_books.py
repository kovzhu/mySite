"""
Script to import book photos from Douban album to the website.
"""

import os
import shutil
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mySite.app import app, db, BookPhoto

SOURCE_DIR = "/Users/k/Library/Mobile Documents/com~apple~CloudDocs/08_Python/Working projects/douban/douban_album/Books"
DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mySite/static/book_photos")

def import_books():
    # Ensure destination directory exists
    os.makedirs(DEST_DIR, exist_ok=True)
    
    print(f"Scanning source directory: {SOURCE_DIR}")
    
    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    print(f"Found {len(files)} images.")
    
    with app.app_context():
        count = 0
        for filename in files:
            # Check if already exists in DB
            if BookPhoto.query.filter_by(filename=filename).first():
                print(f"Skipping {filename} (already in DB)")
                continue
                
            # Copy file
            src_path = os.path.join(SOURCE_DIR, filename)
            dest_path = os.path.join(DEST_DIR, filename)
            
            try:
                shutil.copy2(src_path, dest_path)
            except Exception as e:
                print(f"Error copying {filename}: {e}")
                continue
            
            # Create DB entry
            # Use filename as title, removing extension
            title = os.path.splitext(filename)[0]
            
            book = BookPhoto(
                title=title,
                filename=filename,
                description="Imported from Douban album",
                created_at=datetime.utcnow()
            )
            
            db.session.add(book)
            count += 1
            
            if count % 10 == 0:
                db.session.commit()
                print(f"Imported {count} books...")
        
        db.session.commit()
        print(f"Successfully imported {count} new books!")

if __name__ == "__main__":
    import_books()
