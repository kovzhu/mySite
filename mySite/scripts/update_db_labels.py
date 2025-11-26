import os
import sys
import random

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from mySite.app import app, db, Label, Post

def update_db():
    with app.app_context():
        # Create new tables
        db.create_all()
        print("Database tables updated.")

        # Create dummy labels
        dummy_labels = ["Tech", "Life", "Travel", "Reading", "Thoughts"]
        created_labels = []
        
        for name in dummy_labels:
            label = Label.query.filter_by(name=name).first()
            if not label:
                label = Label(name=name)
                db.session.add(label)
                print(f"Created label: {name}")
            else:
                print(f"Label exists: {name}")
            created_labels.append(label)
        
        db.session.commit()

        # Assign random labels to existing posts if they have none
        posts = Post.query.all()
        for post in posts:
            if not post.labels:
                # Assign 1-2 random labels
                labels_to_add = random.sample(created_labels, k=random.randint(1, 2))
                post.labels.extend(labels_to_add)
                print(f"Assigned labels {labels_to_add} to post '{post.title}'")
        
        db.session.commit()
        print("Dummy data added.")

if __name__ == "__main__":
    update_db()
