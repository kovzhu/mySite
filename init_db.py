#!/usr/bin/env python3
"""
Database initialization script for the Flask application.
Run this script to create the database tables before starting the application.
"""

import os
from app import app, db

def init_database():
    """Initialize the database with required tables."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        print("✅ Database initialization complete!")

if __name__ == '__main__':
    init_database()
