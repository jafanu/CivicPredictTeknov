import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'civic_predict.db')

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-secret-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
