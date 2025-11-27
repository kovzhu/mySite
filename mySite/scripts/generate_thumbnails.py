
import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mySite.app import app

def generate_thumbnails():
    with app.app_context():
        gallery_dir = app.config["PHOTO_UPLOAD_FOLDER"]
        thumbnails_dir = os.path.join(gallery_dir, "thumbnails")
        
        print(f"Gallery Directory: {gallery_dir}")
        print(f"Thumbnails Directory: {thumbnails_dir}")
        
        # Create thumbnails directory if it doesn't exist
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Iterate through year folders
        for item in os.listdir(gallery_dir):
            year_dir = os.path.join(gallery_dir, item)
            
            # Check if it's a directory and looks like a year (4 digits)
            if os.path.isdir(year_dir) and item.isdigit() and len(item) == 4 and item != "thumbnails":
                year = item
                print(f"Processing year: {year}")
                
                # Create year directory in thumbnails
                thumb_year_dir = os.path.join(thumbnails_dir, year)
                os.makedirs(thumb_year_dir, exist_ok=True)
                
                # Process files in the year directory
                for filename in os.listdir(year_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        source_file = os.path.join(year_dir, filename)
                        dest_file = os.path.join(thumb_year_dir, filename)
                        
                        # Skip if thumbnail already exists
                        if os.path.exists(dest_file):
                            continue
                            
                        try:
                            with Image.open(source_file) as img:
                                # Convert to RGB if necessary
                                if img.mode in ("RGBA", "LA", "P"):
                                    img = img.convert("RGB")
                                
                                # Calculate thumbnail size (e.g., 400x400 max)
                                img.thumbnail((400, 400))
                                
                                # Save thumbnail
                                img.save(dest_file, "JPEG", quality=80, optimize=True)
                                print(f"  Generated thumbnail: {filename}")
                        except Exception as e:
                            print(f"  Error processing {filename}: {e}")

        # Also process root level images (legacy)
        print("Processing root level images...")
        for filename in os.listdir(gallery_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                source_file = os.path.join(gallery_dir, filename)
                dest_file = os.path.join(thumbnails_dir, filename)
                
                if os.path.exists(dest_file):
                    continue
                    
                try:
                    with Image.open(source_file) as img:
                        if img.mode in ("RGBA", "LA", "P"):
                            img = img.convert("RGB")
                        img.thumbnail((400, 400))
                        img.save(dest_file, "JPEG", quality=80, optimize=True)
                        print(f"  Generated thumbnail: {filename}")
                except Exception as e:
                    print(f"  Error processing {filename}: {e}")

if __name__ == "__main__":
    generate_thumbnails()
