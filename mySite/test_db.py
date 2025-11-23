#!/usr/bin/env python3
"""
Test script to verify database functionality.
"""

from app import app, db, Project, Post

def test_database():
    """Test database connectivity and table existence."""
    with app.app_context():
        try:
            # Test if we can query the tables
            projects_count = Project.query.count()
            posts_count = Post.query.count()
            
            print(f"✅ Database connection successful!")
            print(f"✅ Projects table: {projects_count} records")
            print(f"✅ Posts table: {posts_count} records")
            
            # Test creating a sample post
            if posts_count == 0:
                sample_post = Post(title="Test Post", content="This is a test post.")
                db.session.add(sample_post)
                db.session.commit()
                print("✅ Created sample post successfully!")
            
        except Exception as e:
            print(f"❌ Database error: {e}")

if __name__ == '__main__':
    test_database()
