import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model settings
    MODEL_NAME = os.getenv('MODEL_NAME', 'cointegrated/rubert-tiny')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/models/sentiment_model')
    MAX_LENGTH = int(os.getenv('MAX_LENGTH', 128))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 16))
    LEARNING_RATE = float(os.getenv('LEARNING_RATE', 2e-5))
    EPOCHS = int(os.getenv('EPOCHS', 3))

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