#!/usr/bin/env python3
"""
Script to create sample projects and posts for the portfolio website.
"""

from app import app, db, Project, Post
from datetime import datetime

def create_sample_data():
    """Create sample projects and posts for the portfolio."""
    with app.app_context():
        # Clear existing data
        Project.query.delete()
        Post.query.delete()
        
        # Create sample projects
        projects = [
            Project(
                title="Portfolio Website",
                description="A responsive Flask-based portfolio website with blog functionality, built using Bootstrap 5 and SQLite database.",
                url="https://github.com/yourusername/portfolio",
                year=2024
            ),
            Project(
                title="Data Analysis Dashboard",
                description="Interactive dashboard for visualizing financial data using Python, Pandas, and Plotly.",
                url="https://github.com/yourusername/data-dashboard",
                year=2023
            ),
            Project(
                title="Machine Learning API",
                description="RESTful API for machine learning predictions built with FastAPI and deployed on AWS.",
                url="https://github.com/yourusername/ml-api",
                year=2023
            ),
            Project(
                title="E-commerce Platform",
                description="Full-stack e-commerce application with user authentication, payment processing, and inventory management.",
                url="https://github.com/yourusername/ecommerce",
                year=2022
            )
        ]
        
        # Create sample posts
        posts = [
            Post(
                title="Welcome to My Portfolio!",
                content="Welcome to my personal portfolio website! I'm excited to share my projects and thoughts with you. This site was built using Flask, SQLite, and Bootstrap 5. Feel free to explore my work and read my latest updates.",
                created_at=datetime(2024, 11, 20)
            ),
            Post(
                title="New Project: Data Analysis Dashboard",
                content="I just launched a new data analysis dashboard that helps visualize financial trends. The project uses Python with Pandas for data processing and Plotly for interactive visualizations. Check out the GitHub repository for more details!",
                created_at=datetime(2024, 11, 15)
            ),
            Post(
                title="Learning FastAPI",
                content="Recently been diving into FastAPI for building high-performance APIs. The automatic documentation and type hints make development so much faster. Planning to migrate some Flask projects to FastAPI soon.",
                created_at=datetime(2024, 11, 10)
            )
        ]
        
        # Add all data to database
        for project in projects:
            db.session.add(project)
        
        for post in posts:
            db.session.add(post)
        
        db.session.commit()
        
        print(f"✅ Created {len(projects)} sample projects")
        print(f"✅ Created {len(posts)} sample posts")
        print("✅ Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()
