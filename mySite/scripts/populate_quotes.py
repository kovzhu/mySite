
import sqlite3
import json
import os
from bs4 import BeautifulSoup

# Configuration
DB_PATH = '../database.db'
JSON_PATH = '../static/rotating_texts.json'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def extract_quotes():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find posts starting with "Fragmented Thoughts"
    cursor.execute("SELECT title, content FROM post WHERE title LIKE 'Fragmented Thoughts%'")
    posts = cursor.fetchall()
    
    new_quotes = []
    
    for post in posts:
        print(f"Processing: {post['title']}")
        content = post['content']
        
        # Parse HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract text from paragraphs
        # We assume each <p> is a quote, or just split text by newlines if no <p> tags found
        paragraphs = soup.find_all('p')
        
        if paragraphs:
            for p in paragraphs:
                text = p.get_text().strip()
                if text:
                    new_quotes.append({
                        "text": text,
                        "author": "K." # Default author for blog posts
                    })
        else:
            # Fallback for plain text or non-p HTML
            text_content = soup.get_text()
            lines = text_content.split('\n')
            for line in lines:
                text = line.strip()
                if text:
                    new_quotes.append({
                        "text": text,
                        "author": "K."
                    })
                    
    conn.close()
    return new_quotes

def update_json(new_quotes):
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"paragraphs": [], "rotationInterval": 5000, "fadeTransitionDuration": 800}
        
    # Append new quotes
    # Optional: Avoid duplicates
    existing_texts = {q['text'] for q in data.get('paragraphs', [])}
    
    added_count = 0
    for quote in new_quotes:
        if quote['text'] not in existing_texts:
            data['paragraphs'].append(quote)
            existing_texts.add(quote['text'])
            added_count += 1
            
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Added {added_count} new quotes.")

if __name__ == "__main__":
    # Ensure we are in the scripts directory or adjust paths
    # The paths are relative to the script location assuming it's run from scripts/
    
    # Check if we need to adjust paths based on CWD
    if not os.path.exists(DB_PATH):
        # Try absolute paths or adjust based on where we think we are
        # But for now, let's assume we run it from mySite/scripts
        pass

    quotes = extract_quotes()
    update_json(quotes)
