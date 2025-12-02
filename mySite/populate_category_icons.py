"""
Script to populate CategoryIcon table with existing book categories and assign icons.
Run this once after creating the CategoryIcon table via migration.
"""

import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Book, CategoryIcon

# Icon mapping based on category names
ICON_MAPPING = {
    'Philosophy and religion': '🧘',
    'Philosophy': '🧘',
    'Religion': '🧘',
    'History': '📜',
    'Science': '🔬',
    'Literature': '📖',
    'Python': '💻',
    'Programming': '💻',
    'Power BI': '📊',
    'Biography': '👤',
    'Psychology and spiritual': '🧠',
    'Psychology': '🧠',
    'Economist': '💰',
    'Economics': '💰',
    'Investing': '💰',
    'Social': '👥',
    'Medical and health': '⚕️',
    'Medicine': '⚕️',
    'China classical': '🏮',
    'Chinese': '🏮',
    'General non-fiction': '📚',
    'Humanistic and art': '🎨',
    'Art': '🎨',
    'Learning': '📝',
    'Education': '📝',
    'Work related': '💼',
    'Business': '💼',
    'Politics': '⚖️',
}

def get_icon_for_category(category_name):
    """Get an appropriate icon for a category based on its name."""
    # Try exact match first
    if category_name in ICON_MAPPING:
        return ICON_MAPPING[category_name]
    
    # Try partial match
    category_lower = category_name.lower()
    for key, icon in ICON_MAPPING.items():
        if key.lower() in category_lower or category_lower in key.lower():
            return icon
    
    # Default icon
    return '📚'

def populate_categories():
    """Populate CategoryIcon table with existing book categories."""
    with app.app_context():
        # Get all distinct categories from books
        categories = db.session.query(Book.category).distinct().all()
        category_names = sorted([c[0] for c in categories])
        
        print(f"Found {len(category_names)} categories in the Book table:")
        for name in category_names:
            print(f"  - {name}")
        
        print("\nPopulating CategoryIcon table...")
        
        for i, name in enumerate(category_names):
            # Check if category already exists
            existing = CategoryIcon.query.filter_by(name=name).first()
            if existing:
                print(f"  ✓ Category '{name}' already exists with icon {existing.icon}")
                continue
            
            icon = get_icon_for_category(name)
            new_category = CategoryIcon(
                name=name,
                icon=icon,
                display_order=i
            )
            db.session.add(new_category)
            print(f"  + Adding category '{name}' with icon {icon}")
        
        db.session.commit()
        print("\n✅ CategoryIcon table populated successfully!")
        
        # Display summary
        all_categories = CategoryIcon.query.order_by(CategoryIcon.display_order).all()
        print(f"\nTotal categories in CategoryIcon table: {len(all_categories)}")
        print("\nFinal category list:")
        for cat in all_categories:
            book_count = Book.query.filter_by(category=cat.name).count()
            print(f"  {cat.icon} {cat.name} ({book_count} books)")

if __name__ == '__main__':
    populate_categories()
