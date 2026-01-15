import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

    # Services
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth:5000')
    COLLECTOR_SERVICE_URL = os.getenv('COLLECTOR_SERVICE_URL', 'http://collector:5001')

    # PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'reviewsdb')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

    # MongoDB
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_DB = os.getenv('MONGO_DB', 'reviews')
    MONGO_USER = os.getenv('MONGO_USER', 'mongo')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'mongo')

    @staticmethod
    def get_mongo_url():
        return f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:{Config.MONGO_PORT}"