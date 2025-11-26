import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Add the project root to Python path
# Script is in mySite/mySite/scripts/import_douban.py
# We want to add .../mySite/ to path so we can do 'from mySite.app import ...'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from mySite.app import app, db, Post


def parse_douban_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    notes = []
    
    # Strategy 1: Look for the downloaded format (h1, .meta, .note)
    if soup.select_one('h1') and soup.select_one('.meta'):
        try:
            # Title
            title = soup.select_one('h1').get_text(strip=True)
            
            # Content
            content_tag = soup.select_one('.note')
            content = str(content_tag) if content_tag else ""
            
            # Date
            created_at = datetime.utcnow()
            meta_div = soup.select_one('.meta')
            if meta_div:
                # Look for the div containing "发布时间"
                for div in meta_div.find_all('div'):
                    text = div.get_text(strip=True)
                    if "发布时间" in text:
                        # Extract date using regex
                        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', text)
                        if match:
                            try:
                                created_at = datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                pass
                        break
            
            notes.append({
                'title': title,
                'content': content,
                'created_at': created_at
            })
        except Exception as e:
            print(f"Error parsing downloaded note {os.path.basename(file_path)}: {e}")

    # Strategy 2: Look for original Douban page structure (fallback)
    elif soup.select_one('.note-header h1'):
        # ... (keep existing logic)
        try:
            # Title
            title = soup.select_one('.note-header h1').get_text(strip=True)
            
            # Content
            content_tag = soup.select_one('#link-report .note')
            if content_tag:
                for script in content_tag.select('script'):
                    script.decompose()
                content = str(content_tag)
            else:
                content = ""
            
            # Date
            date_tag = soup.select_one('.pub-date')
            created_at = datetime.utcnow()
            if date_tag:
                date_str = date_tag.get_text(strip=True)
                match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str)
                if match:
                    try:
                        created_at = datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass

            notes.append({
                'title': title,
                'content': content,
                'created_at': created_at
            })
        except Exception as e:
            print(f"Error parsing single note {os.path.basename(file_path)}: {e}")
            
    else:
        print(f"Failed to detect note structure in {os.path.basename(file_path)}")
        pass
            
    return notes

def import_notes():
    source_dir = "/Users/k/Library/Mobile Documents/com~apple~CloudDocs/08_Python/Working projects/douban/douban_blog"
    
    if not os.path.exists(source_dir):
        print(f"Error: Source directory not found: {source_dir}")
        return

    files = [f for f in os.listdir(source_dir) if f.endswith('.html')]
    
    if not files:
        print(f"No .html files found in {source_dir}")
        return

    print(f"Found {len(files)} HTML files to process.")
    total_imported = 0
    skipped_count = 0
    
    with app.app_context():
        for filename in files:
            file_path = os.path.join(source_dir, filename)
            # print(f"Processing {filename}...")
            
            notes = parse_douban_html(file_path)
            
            if not notes:
                # print(f"No notes found in {filename}")
                continue

            for note in notes:
                # Check for duplicates
                if Post.query.filter_by(title=note['title']).first():
                    # print(f"Skipping duplicate: {note['title']}")
                    skipped_count += 1
                    continue
                
                new_post = Post(
                    title=note['title'],
                    content=note['content'],
                    created_at=note['created_at']
                )
                db.session.add(new_post)
                total_imported += 1
                print(f"Imported: {note['title']}")
                
        db.session.commit()
        print(f"\nSummary:")
        print(f"Successfully imported: {total_imported}")
        print(f"Skipped (duplicates): {skipped_count}")

if __name__ == "__main__":
    import_notes()
