import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_DB = os.getenv('MONGO_DB', 'social_media')
    MONGO_USER = os.getenv('MONGO_USER', 'admin')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password123')

    @staticmethod
    def get_mongo_url():
        return f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:{Config.MONGO_PORT}/"

    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'analytics_db')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres123')

    @staticmethod
    def get_postgres_url():
        return f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"

    SECRET_KEY = os.getenv('SECRET_KEY', '7K2mP9nQ3xR8zW5vL1tY4cB6hN0fG2sD7aE9qW3uI5oX8jM1kL4pR6')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'Z9xC2vB7nM4kL1jH3gF8dS0aP5oI6uY2tR4eW9qA1sD3fG7hJ5kN8')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

    COLLECTOR_HOST = os.getenv('COLLECTOR_HOST', 'collector')
    COLLECTOR_PORT = int(os.getenv('COLLECTOR_PORT', 5001))

    @staticmethod
    def get_collector_url():
        return f"http://{Config.COLLECTOR_HOST}:{Config.COLLECTOR_PORT}"

    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5002))

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'