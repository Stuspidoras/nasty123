@api_bp.route('/search/queries', methods=['GET'])
@token_required
def get_user_search_queries(current_user_id):
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, search_query, sources, status, 
                   created_at, completed_at, total_found
            FROM search_queries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 50
        """, (current_user_id,))

        queries = []
        for row in cur.fetchall():
            queries.append({
                'id': row[0],
                'search_query': row[1],
                'sources': row[2],
                'status': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'completed_at': row[5].isoformat() if row[5] else None,
                'total_found': row[6]
            })

        cur.close()
        conn.close()

        return jsonify({
            'queries': queries,
            'total': len(queries)
        }), 200
    except Exception as e:
        logger.error(f"Ошибка получения запросов: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/search/create', methods=['POST'])
@token_required
def create_search_query(current_user_id):
    data = request.get_json()

    search_query = data.get('search_query', '').strip()
    sources = data.get('sources', ['vk', 'ok'])
    count = data.get('count', 100)

    if not search_query:
        return jsonify({'error': 'Необходимо указать поисковый запрос'}), 400

    try:
        # Сохраняем запрос в БД
        conn = get_postgres_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO search_queries (user_id, search_query, sources, status)
            VALUES (%s, %s, %s, 'pending')
            RETURNING id
        """, (current_user_id, search_query, sources))

        query_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        # Отправляем запрос в collector
        import requests
        response = requests.post(
            f'http://{Config.COLLECTOR_HOST}:{Config.COLLECTOR_PORT}/api/collect',
            json={
                'search_query': search_query,
                'sources': sources,
                'count': count
            }
        )

        if response.status_code in [200, 202]:
            return jsonify({
                'message': 'Поиск запущен',
                'query_id': query_id,
                'search_query': search_query,
                'collector_response': response.json()
            }), 202
        else:
            return jsonify({'error': 'Ошибка запуска сбора данных'}), 500

    except Exception as e:
        logger.error(f"Ошибка создания запроса: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/posts/by-search', methods=['GET'])
@token_required
def get_posts_by_search_query(current_user_id):
    search_query = request.args.get('search_query', '')
    sentiment = request.args.get('sentiment', '')
    source = request.args.get('source', '')
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))

    if not search_query:
        return jsonify({'error': 'Необходимо указать search_query'}), 400

    filter_query = {'original_search_query': search_query}

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

        for post in posts:
            post['_id'] = str(post['_id'])
            if 'date' in post:
                post['date'] = post['date'].isoformat() if hasattr(post['date'], 'isoformat') else str(post['date'])
            if 'collected_at' in post:
                post['collected_at'] = post['collected_at'].isoformat() if hasattr(post['collected_at'], 'isoformat') else str(post['collected_at'])

        total = mongo_db.processed_posts.count_documents(filter_query)

        return jsonify({
            'search_query': search_query,
            'posts': posts,
            'total': total,
            'limit': limit,
            'skip': skip
        }), 200
    except Exception as e:
        logger.error(f"Ошибка получения постов: {e}")
        return jsonify({'error': str(e)}), 500