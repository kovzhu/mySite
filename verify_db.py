import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mySite.app import app, db, Photo, Post

with app.app_context():
    photo_count = Photo.query.count()
    post_count = Post.query.count()
    print(f"Photos: {photo_count}")
    print(f"Posts: {post_count}")
    
    if photo_count > 0:
        print("\nRecent Photos:")
        for p in Photo.query.order_by(Photo.created_at.desc()).limit(3).all():
            print(f"- {p.title} ({p.filename})")
            
    if post_count > 0:
        print("\nRecent Posts:")
        for p in Post.query.order_by(Post.created_at.desc()).limit(3).all():
            print(f"- {p.title}")
