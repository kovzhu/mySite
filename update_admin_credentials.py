#!/usr/bin/env python3
"""
Script to update the admin user credentials.
This will change the admin username to 'k' and password to 'kov1210'
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User

def update_admin_credentials():
    """Update admin user credentials to the specified username and password."""
    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Admin user not found! Creating new admin user...")
            admin_user = User(
                username='k',
                email='k@example.com',
                role='admin'
            )
        else:
            print("Found existing admin user, updating credentials...")
            admin_user.username = 'k'
            admin_user.email = 'k@example.com'
        
        # Set the new password
        admin_user.set_password('kov1210')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Admin credentials updated successfully!")
        print("New credentials:")
        print("Username: k")
        print("Password: kov1210")
        print("Email: k@example.com")

if __name__ == "__main__":
    update_admin_credentials()
