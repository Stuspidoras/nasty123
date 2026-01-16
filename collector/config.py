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

    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    @staticmethod
    def get_redis_url():
        """Формирует URL подключения к Redis"""
        return f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/{Config.REDIS_DB}"

    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN', 'vk1.a.vO41FWwmBwskdldfiDApCearfAxsLbu85xqPbSdcL691Jjx0vRJMs7PJJ0WAtFpBVXSnhenU0XmYVmvO_ZL4vFHl3Oe11VUQ9pIOhdXdZh-hFpI15VY3j4Yb42ofY2qX2u4OVhOSGwfhnYeCbtP5MOA6crnIBnmUv9PSkcHGjbL4w1tSXpje-MPo1qjY5tXsHY7nMzrKDSnCPAvosZTFww')
    VK_API_VERSION = os.getenv('VK_API_VERSION', '5.131')

    OK_ACCESS_TOKEN = os.getenv('OK_ACCESS_TOKEN', '-n-YIVrMkrCimDEowZvkTn7mRr7CeUDeQnovFk0Wt1TH7uO0kdl2Umgevry0aQt16SZpTAuCvoYbbFxPAzrn')
    OK_APPLICATION_KEY = os.getenv('OK_APPLICATION_KEY', 'CJFFBCOGDIHBABAB')
    OK_SESSION_SECRET_KEY = os.getenv('OK_SESSION_SECRET_KEY', '7b2504d0b56e9b87181eabd2bdb9691e')

    CELERY_BROKER_URL = get_redis_url.__func__()
    CELERY_RESULT_BACKEND = get_redis_url.__func__()
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Moscow'
    CELERY_ENABLE_UTC = True

    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5001))

    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 60))

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'