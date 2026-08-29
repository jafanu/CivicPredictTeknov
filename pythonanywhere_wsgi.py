"""
WSGI entry point for PythonAnywhere deployment.

Steps:
1. Upload this repo to PythonAnywhere (via git or Files tab)
2. Go to Web tab → Add new web app → Manual configuration → Python 3.10
3. Set WSGI configuration file to point here
4. In the WSGI file, replace the default with:
"""
import sys
import os

# Add your project directory to sys.path
project_home = os.path.expanduser('~/civic-predict-ai')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app
from app import app as application

# Ensure the database is initialized
db_path = os.path.join(project_home, 'civic_predict.db')
if not os.path.exists(db_path):
    from init_db import init_db
    init_db()
