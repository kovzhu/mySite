import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
import re


# Add the parent directory to Python path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mySite.app import app, db, Post


def parse_douban_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    notes = []
    
    # Strategy: Look for single note page structure first
    if soup.select_one('.note-header h1'):
        print(f"Detected single note page: {file_path}")
        try:
            # Title
            title = soup.select_one('.note-header h1').get_text(strip=True)
            
            # Content
            content_tag = soup.select_one('#link-report .note')
            content = str(content_tag) if content_tag else ""
            
            # Date
            date_tag = soup.select_one('.pub-date')
            created_at = datetime.utcnow()
            if date_tag:
                date_str = date_tag.get_text(strip=True)
                # Format: 2024-06-29 14:56:55 (ignore extra text like location)
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
            print(f"Error parsing single note: {e}")
            
    else:
        # Fallback to list page structure
        note_items = soup.select('.note-container') or soup.select('.article')
        print(f"Found {len(note_items)} potential notes in list: {file_path}")
        
        for item in note_items:
            try:
                # Title
                title_tag = item.select_one('h3 a') or item.select_one('.title a')
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                
                # Content (Summary or Full)
                content_tag = item.select_one('.note-content') or item.select_one('.content')
                content = str(content_tag) if content_tag else ""
                
                # Date
                date_tag = item.select_one('.pub-date') or item.select_one('.time')
                created_at = datetime.utcnow()
                if date_tag:
                    date_str = date_tag.get_text(strip=True)
                    try:
                        created_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            created_at = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            pass 
                
                notes.append({
                    'title': title,
                    'content': content,
                    'created_at': created_at
                })
                
            except Exception as e:
                print(f"Error parsing a note: {e}")
            
    return notes

def import_notes():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    files = [f for f in os.listdir(base_dir) if f.startswith('douban_') and f.endswith('.html')]
    
    if not files:
        print("No 'douban_*.html' files found in the project root.")
        print("Please save your Douban notes pages as douban_1.html, douban_2.html, etc.")
        return

    total_imported = 0
    
    with app.app_context():
        for filename in files:
            file_path = os.path.join(base_dir, filename)
            print(f"Processing {filename}...")
            
            notes = parse_douban_html(file_path)
            
            for note in notes:
                # Check for duplicates
                if Post.query.filter_by(title=note['title']).first():
                    print(f"Skipping duplicate: {note['title']}")
                    continue
                
                new_post = Post(
                    title=note['title'],
                    content=note['content'],
                    created_at=note['created_at']
                )
                db.session.add(new_post)
                total_imported += 1
                
        db.session.commit()
        print(f"\nSuccessfully imported {total_imported} notes!")

if __name__ == "__main__":
    import_notes()
