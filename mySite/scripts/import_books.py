
import os
import shutil
import sys
from datetime import datetime

# Add parent directory to path to import app and db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, Book

SOURCE_DIR = "/Users/k/Library/Mobile Documents/com~apple~CloudDocs/02_Books"
DEST_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/library_books'))

EXCLUDED_DIRS = {'Audio', '.DS_Store'}

def import_books():
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        return

    # Ensure destination base directory exists
    os.makedirs(DEST_BASE_DIR, exist_ok=True)

    with app.app_context():
        # Iterate through categories
        for item in os.listdir(SOURCE_DIR):
            category_path = os.path.join(SOURCE_DIR, item)
            
            # Skip excluded directories and files
            if item in EXCLUDED_DIRS or item.startswith('.') or not os.path.isdir(category_path):
                continue
                
            category_name = item
            print(f"Processing category: {category_name}")
            
            # Create category directory in static
            dest_category_dir = os.path.join(DEST_BASE_DIR, category_name)
            os.makedirs(dest_category_dir, exist_ok=True)
            
            # Recursively walk through the category directory
            for root, dirs, files in os.walk(category_path):
                # Remove excluded directories from dirs list to prevent walking into them
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
                
                for filename in files:
                    if filename.startswith('.') or filename == '.DS_Store':
                        continue
                        
                    file_path = os.path.join(root, filename)
                    
                    # Copy file to category directory (flatten structure)
                    dest_file_path = os.path.join(dest_category_dir, filename)
                    
                    # Handle duplicate filenames by adding number suffix
                    if os.path.exists(dest_file_path) and os.path.getsize(file_path) != os.path.getsize(dest_file_path):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while os.path.exists(dest_file_path):
                            new_filename = f"{base}_{counter}{ext}"
                            dest_file_path = os.path.join(dest_category_dir, new_filename)
                            counter += 1
                        filename = os.path.basename(dest_file_path)
                    
                    # Only copy if it doesn't exist
                    if not os.path.exists(dest_file_path):
                        print(f"  Copying: {filename}")
                        shutil.copy2(file_path, dest_file_path)
                    
                    # Create/Update database entry
                    # Relative path for database
                    rel_path = f"library_books/{category_name}/{filename}"
                    
                    # Try to parse author and title from filename
                    # Common formats: "Author - Title.ext", "Title.ext"
                    name_without_ext = os.path.splitext(filename)[0]
                    if ' - ' in name_without_ext:
                        parts = name_without_ext.split(' - ', 1)
                        author = parts[0].strip()
                        title = parts[1].strip()
                    else:
                        author = "Unknown"
                        title = name_without_ext
                    
                    # Check if book already exists in DB
                    existing_book = Book.query.filter_by(filename=filename, category=category_name).first()
                    
                    if not existing_book:
                        print(f"  Adding to DB: {title}")
                        new_book = Book(
                            title=title,
                            author=author,
                            category=category_name,
                            filename=filename,
                            file_path=rel_path,
                            description="", # Can be updated manually later
                            upload_date=datetime.utcnow()
                        )
                        db.session.add(new_book)
        
        db.session.commit()
        print("Import completed.")

if __name__ == "__main__":
    import_books()
