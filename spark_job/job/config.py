import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Spark
    SPARK_MASTER = os.getenv('SPARK_MASTER', 'spark://spark-master:7077')
    SPARK_APP_NAME = 'ReviewAnalytics'

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

    # Paths
    MODEL_PATH = os.getenv('MODEL_PATH', '/app/models')

    @staticmethod
    def get_postgres_url():
        return f"jdbc:postgresql://{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"

    @staticmethod
    def get_mongo_url():
        return f"mongodb://{Config.MONGO_USER}:{Config.MONGO_PASSWORD}@{Config.MONGO_HOST}:{Config.MONGO_PORT}"