#!/usr/bin/env python3
"""
Quick launcher for the customer support frontend demo
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Customer Support Frontend...")
    print("📍 This demonstrates what Lab 5 (Multi-Agent Frontend) would look like")
    print()
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installed")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_path = os.path.join(script_dir, "frontend_demo.py")
    
    print(f"🌐 Starting frontend at: http://localhost:8501")
    print("💡 This shows how customers would interact with your multi-agent system")
    print()
    
    # Run streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", frontend_path,
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

if __name__ == "__main__":
    main()