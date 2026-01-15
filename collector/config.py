import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # VK API
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN', '')
    VK_API_VERSION = '5.131'

    # OK API
    OK_ACCESS_TOKEN = os.getenv('OK_ACCESS_TOKEN', '')
    OK_APPLICATION_KEY = os.getenv('OK_APPLICATION_KEY', '')
    OK_SESSION_SECRET_KEY = os.getenv('OK_SESSION_SECRET_KEY', '')

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

    # Redis для очереди задач
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

    @staticmethod
    def get_mongo_url():
        return f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:{Config.MONGO_PORT}"