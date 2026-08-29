import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'civic_predict.db')
SECRET_KEY = 'civic-predict-ai-2026-secret-key'
DEBUG = True
