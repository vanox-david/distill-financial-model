#!/usr/bin/env python3
"""
Redirect file for backward compatibility with Streamlit Cloud deployment.

This file maintains the original filename that Streamlit Cloud expects
while redirecting to the new modular main.py structure.

This is a common pattern for maintaining deployment compatibility
after refactoring.
"""

# Import and run the main application
if __name__ == "__main__":
    from main import main
    main() 