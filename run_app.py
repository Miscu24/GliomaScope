#!/usr/bin/env python3
"""
GliomaScope Web Application Startup Script
"""

import sys
import subprocess
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("ERROR: Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"SUCCESS: Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 
        'plotly', 'umap-learn', 'scipy', 'statsmodels'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"SUCCESS: {package}")
        except ImportError:
            print(f"ERROR: {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nERROR: Missing packages: {', '.join(missing_packages)}")
        print("Please install dependencies using:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['uploads', 'cleaned_data', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def main():
    print("GENE: GliomaScope Web Application")
    print("=" * 40)
    
    # Check Python version
    print("\n1. Checking Python version...")
    check_python_version()
    
    # Check dependencies
    print("\n2. Checking dependencies...")
    check_dependencies()
    
    # Create directories
    print("\n3. Setting up directories...")
    create_directories()
    
    # Start the application
    print("\n4. Starting GliomaScope...")
    print("The application will be available at: http://localhost:5002")
    print("For help, see README.md")
    print("Press Ctrl+C to stop the application")
    print("=" * 40)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5002)
    except KeyboardInterrupt:
        print("\nGliomaScope stopped by user")
    except Exception as e:
        print(f"\nERROR: Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 