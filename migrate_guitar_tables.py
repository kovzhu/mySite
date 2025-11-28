"""
Database migration script to add Guitar collection tables.
Run this script to create the GuitarVideo and GuitarPhoto tables.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mySite.app import app, db

def migrate_database():
    """Create new tables for Guitar collection."""
    with app.app_context():
        print("Creating new tables for Collections...")
        db.create_all()
        print("✓ Database tables created successfully!")
        print("  - GuitarVideo table")
        print("  - GuitarPhoto table")
        print("  - CollectionVideo table")
        print("  - BookPhoto table")
        print("  - ExercisePhoto table")
        print("  - ReadingQuotePhoto table")
        print("  - IntellectualPhoto table")
        print("  - FragmentedQuotePhoto table")

if __name__ == "__main__":
    migrate_database()
