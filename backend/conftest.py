# conftest.py
# Adds backend root to Python path so pytest finds modules automatically.
import sys, os
sys.path.insert(0, os.path.dirname(__file__))