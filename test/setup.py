#!/usr/bin/env python3
"""
Setup script for AI Insights Agent MVP
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        return False
    print(f"SUCCESS: Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("SUCCESS: Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    env_content = """# Google Cloud API Configuration
# Replace with your actual Google API key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Google Cloud Project ID
# GOOGLE_CLOUD_PROJECT=your_project_id
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_content)
        print("SUCCESS: Created .env file template")
        print("   Please edit .env and add your GOOGLE_API_KEY")
    else:
        print("SUCCESS: .env file already exists")

def run_tests():
    """Run structure tests"""
    print("\nRunning structure tests...")
    try:
        subprocess.check_call([sys.executable, "test_structure.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("AI Insights Agent MVP - Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create .env file
    create_env_file()
    
    # Run tests
    if not run_tests():
        return 1
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your GOOGLE_API_KEY")
    print("2. Run: python run_analysis.py")
    print("3. Review the generated insights")
    
    return 0

if __name__ == "__main__":
    exit(main())
