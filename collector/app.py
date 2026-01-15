from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from pymongo import MongoClient
from vk_collector import VKCollector
from ok_collector import OKCollector
from config import Config
from celery import Celery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Celery для асинхронной обработки
celery = Celery('collector', broker=f'redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}/0')

# MongoDB подключение
mongo_client = MongoClient(Config.get_mongo_url())
mongo_db = mongo_client[Config.MONGO_DB]

def get_postgres_connection():
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT,
        database=Config.POSTGRES_DB,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD
    )

@celery.task
def collect_reviews_task(sources, keywords, count=100):
    """
    Асинхронная задача сбора отзывов
    """
    vk_collector = VKCollector()
    ok_collector = OKCollector()

    all_posts = []

    for keyword in keywords:
        if 'vk' in sources:
            vk_posts = vk_collector.search_posts(keyword, count)
            all_posts.extend(vk_posts)

            # Получение комментариев к постам
            for post in vk_posts[:10]:  # Ограничение для примера
                comments = vk_collector.get_comments(
                    post['owner_id'],
                    post['post_id'],
                    count=50
                )
                post['comments'] = comments

        if 'ok' in sources:
            ok_posts = ok_collector.search_posts(keyword, count)
            all_posts.extend(ok_posts)

    # Сохранение в MongoDB (для сырых данных)
    if all_posts:
        mongo_db.raw_posts.insert_many(all_posts)
        logger.info(f"Сохранено {len(all_posts)} постов в MongoDB")

    # Сохранение метаданных в PostgreSQL
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()

        for post in all_posts:
            cur.execute("""
                INSERT INTO collected_posts 
                (source, post_id, text, date, likes, comments_count, query)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source, post_id) DO NOTHING
            """, (
                post['source'],
                str(post.get('post_id', '')),
                post['text'],
                post['date'],
                post.get('likes', 0),
                post.get('comments_count', 0),
                post['query']
            ))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"Метаданные сохранены в PostgreSQL")

    except Exception as e:
        logger.error(f"Ошибка при сохранении в PostgreSQL: {e}")

    return {
        'status': 'success',
        'collected': len(all_posts)
    }

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/collect', methods=['POST'])
def collect_reviews():
    """
    Запуск сбора отзывов
    """
    data = request.get_json()

    sources = data.get('sources', ['vk', 'ok'])
    keywords = data.get('keywords', [])
    count = data.get('count', 100)

    if not keywords:
        return jsonify({'error': 'Необходимо указать ключевые слова'}), 400

    # Запуск асинхронной задачи
    task = collect_reviews_task.delay(sources, keywords, count)

    return jsonify({
        'message': 'Сбор данных запущен',
        'task_id': task.id
    }), 202

@app.route('/api/collect/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    Проверка статуса задачи сбора
    """
    task = collect_reviews_task.AsyncResult(task_id)

    return jsonify({
        'task_id': task_id,
        'state': task.state,
        'result': task.result if task.ready() else None
    }), 200

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Получение собранных постов
    """
    query = request.args.get('query', '')
    source = request.args.get('source', '')
    limit = int(request.args.get('limit', 50))

    filter_query = {}
    if query:
        filter_query['query'] = query
    if source:
        filter_query['source'] = source

    posts = list(mongo_db.raw_posts.find(filter_query).limit(limit))

    # Преобразование ObjectId в строку
    for post in posts:
        post['_id'] = str(post['_id'])

    return jsonify({
        'posts': posts,
        'count': len(posts)
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)