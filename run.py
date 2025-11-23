#!/usr/bin/env python3
"""
Simple script to run the Flask application.
This makes it easy to start your website without complex commands.
"""

import os
import sys

# Add the current directory to Python path so we can import mySite
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mySite.app import app
    print("✅ Flask application loaded successfully!")
    print("🚀 Starting server on http://127.0.0.1:8080")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the application
    app.run(debug=True, host='127.0.0.1', port=8080)
    
except ImportError as e:
    print(f"❌ Error importing Flask application: {e}")
    print("\n💡 Try installing dependencies first:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error running Flask application: {e}")
    print("\n🔧 Check if all dependencies are installed:")
    print("   pip install -r requirements.txt")
