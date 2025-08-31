"""
Adaptive Exam Preparation AI - Main Application
Entry point for the Streamlit application with authentication
"""

import streamlit as st
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the main UI
from ui.Home import main

if __name__ == "__main__":
    main()