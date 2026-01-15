from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import psycopg2
from config import Config
import jwt
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

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

def token_required(f):
    """Декоратор для проверки JWT токена"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Токен отсутствует'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data['user_id']

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Токен истёк'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Недействительный токен'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({'status': 'healthy'}), 200

@api_bp.route('/statistics/sentiment', methods=['GET'])
@token_required
def get_sentiment_statistics(current_user_id):
    """
    Получение статистики по тональности
    """
    query = request.args.get('query', '')
    source = request.args.get('source', '')

    try:
        conn = get_postgres_connection()
        cur = conn.cursor()

        sql = """
            SELECT sentiment, source, SUM(count) as total_count
            FROM sentiment_statistics
            WHERE 1=1
        """
        params = []

        if query:
            sql += " AND query = %s"
            params.append(query)

        if source:
            sql += " AND source = %s"
            params.append(source)

        sql += " GROUP BY sentiment, source ORDER BY total_count DESC"

        cur.execute(sql, params)
        results = cur.fetchall()

        statistics = []
        for row in results:
            statistics.append({
                'sentiment': row[0],
                'source': row[1],
                'count': row[2]
            })

        cur.close()
        conn.close()

        return jsonify({
            'statistics': statistics,
            'total': len(statistics)
        }), 200

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/posts/processed', methods=['GET'])
@token_required
def get_processed_posts(current_user_id):
    """
    Получение обработанных постов
    """
    query = request.args.get('query', '')
    sentiment = request.args.get('sentiment', '')
    source = request.args.get('source', '')
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))

    filter_query = {}

    if query:
        filter_query['query'] = query

    if sentiment:
        filter_query['sentiment'] = sentiment

    if source:
        filter_query['source'] = source

    try:
        posts = list(
            mongo_db.processed_posts
            .find(filter_query)
            .skip(skip)
            .limit(limit)
            .sort('collected_at', -1)
        )

        # Преобразование ObjectId в строку
        for post in posts:
            post['_id'] = str(post['_id'])
            if 'date' in post:
                post['date'] = post['date'].isoformat() if hasattr(post['date'], 'isoformat') else str(post['date'])
            if 'collected_at' in post:
                post['collected_at'] = post['collected_at'].isoformat() if hasattr(post['collected_at'], 'isoformat') else str(post['collected_at'])

        total = mongo_db.processed_posts.count_documents(filter_query)

        return jsonify({
            'posts': posts,
            'total': total,
            'limit': limit,
            'skip': skip
        }), 200

    except Exception as e:
        logger.error(f"Ошибка получения постов: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/overview', methods=['GET'])
@token_required
def get_analytics_overview(current_user_id):
    """
    Получение общей аналитики
    """
    query = request.args.get('query', '')

    try:
        filter_query = {}
        if query:
            filter_query['query'] = query

        # Статистика по тональности
        sentiment_pipeline = [
            {'$match': filter_query},
            {'$group': {
                '_id': '$sentiment',
                'count': {'$sum': 1},
                'avg_confidence': {'$avg': '$sentiment_confidence'}
            }}
        ]

        sentiment_stats = list(mongo_db.processed_posts.aggregate(sentiment_pipeline))

        # Статистика по источникам
        source_pipeline = [
            {'$match': filter_query},
            {'$group': {
                '_id': '$source',
                'count': {'$sum': 1}
            }}
        ]

        source_stats = list(mongo_db.processed_posts.aggregate(source_pipeline))

        # Топ ключевых слов
        keywords_pipeline = [
            {'$match': filter_query},
            {'$unwind': '$keywords'},
            {'$group': {
                '_id': '$keywords',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 20}
        ]

        top_keywords = list(mongo_db.processed_posts.aggregate(keywords_pipeline))

        # Временная динамика
        time_pipeline = [
            {'$match': filter_query},
            {'$group': {
                '_id': {
                    'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}},
                    'sentiment': '$sentiment'
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.date': 1}}
        ]

        time_series = list(mongo_db.processed_posts.aggregate(time_pipeline))

        return jsonify({
            'sentiment_distribution': sentiment_stats,
            'source_distribution': source_stats,
            'top_keywords': top_keywords,
            'time_series': time_series
        }), 200

    except Exception as e:
        logger.error(f"Ошибка получения аналитики: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/keywords', methods=['GET'])
@token_required
def get_keyword_analysis(current_user_id):
    """
    Анализ ключевых слов
    """
    query = request.args.get('query', '')
    sentiment = request.args.get('sentiment', '')
    limit = int(request.args.get('limit', 50))

    filter_query = {}

    if query:
        filter_query['query'] = query

    if sentiment:
        filter_query['sentiment'] = sentiment

    try:
        pipeline = [
            {'$match': filter_query},
            {'$unwind': '$keywords'},
            {'$group': {
                '_id': '$keywords',
                'count': {'$sum': 1},
                'sentiments': {'$push': '$sentiment'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]

        keywords = list(mongo_db.processed_posts.aggregate(pipeline))

        # Подсчет распределения тональности для каждого ключевого слова
        for keyword in keywords:
            sentiments = keyword['sentiments']
            keyword['sentiment_distribution'] = {
                'positive': sentiments.count('positive'),
                'negative': sentiments.count('negative'),
                'neutral': sentiments.count('neutral')
            }
            del keyword['sentiments']

        return jsonify({
            'keywords': keywords,
            'total': len(keywords)
        }), 200

    except Exception as e:
        logger.error(f"Ошибка анализа ключевых слов: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/entities', methods=['GET'])
@token_required
def get_entity_analysis(current_user_id):
    """
    Анализ именованных сущностей
    """
    query = request.args.get('query', '')
    limit = int(request.args.get('limit', 50))

    filter_query = {}

    if query:
        filter_query['query'] = query

    try:
        pipeline = [
            {'$match': filter_query},
            {'$unwind': '$entities'},
            {'$group': {
                '_id': {
                    'text': '$entities.text',
                    'label': '$entities.label'
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]

        entities = list(mongo_db.processed_posts.aggregate(pipeline))

        return jsonify({
            'entities': entities,
            'total': len(entities)
        }), 200

    except Exception as e:
        logger.error(f"Ошибка анализа сущностей: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/export/csv', methods=['GET'])
@token_required
def export_to_csv(current_user_id):
    """
    Экспорт данных в CSV
    """
    import csv
    from io import StringIO
    from flask import make_response

    query = request.args.get('query', '')
    sentiment = request.args.get('sentiment', '')

    filter_query = {}

    if query:
        filter_query['query'] = query

    if sentiment:
        filter_query['sentiment'] = sentiment

    try:
        posts = list(mongo_db.processed_posts.find(filter_query).limit(1000))

        # Создание CSV
        si = StringIO()
        cw = csv.writer(si)

        # Заголовки
        cw.writerow(['ID', 'Source', 'Text', 'Sentiment', 'Confidence', 'Date', 'Likes', 'Comments'])

        # Данные
        for post in posts:
            cw.writerow([
                str(post.get('post_id', '')),
                post.get('source', ''),
                post.get('text', ''),
                post.get('sentiment', ''),
                post.get('sentiment_confidence', 0),
                post.get('date', ''),
                post.get('likes', 0),
                post.get('comments_count', 0)
            ])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=reviews_export.csv"
        output.headers["Content-type"] = "text/csv"

        return output

    except Exception as e:
        logger.error(f"Ошибка экспорта: {e}")
        return jsonify({'error': str(e)}), 500