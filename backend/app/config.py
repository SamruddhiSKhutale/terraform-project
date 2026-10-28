import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nexus-tasks-prod-secret-key-change-me-in-production-2024'
    
    # Database - supports both SQLite (dev) and MySQL (production/RDS)
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'nexus')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'NexusSecurePass123!')
    DB_NAME = os.environ.get('DB_NAME', 'nexustasks')
    
    # Use MySQL if DB_HOST is set to something other than localhost/sqlite, else SQLite
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'
    
    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'nexustasks.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
