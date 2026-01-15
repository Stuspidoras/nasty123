// Инициализация MongoDB

db = db.getSiblingDB('reviews');

// Создание коллекций
db.createCollection('raw_posts');
db.createCollection('processed_posts');
db.createCollection('labeled_posts');

// Создание индексов для raw_posts
db.raw_posts.createIndex({ "query": 1 });
db.raw_posts.createIndex({ "source": 1 });
db.raw_posts.createIndex({ "date": -1 });
db.raw_posts.createIndex({ "collected_at": -1 });
db.raw_posts.createIndex({ "post_id": 1, "source": 1 }, { unique: true });

// Создание индексов для processed_posts
db.processed_posts.createIndex({ "query": 1 });
db.processed_posts.createIndex({ "source": 1 });
db.processed_posts.createIndex({ "sentiment": 1 });
db.processed_posts.createIndex({ "date": -1 });
db.processed_posts.createIndex({ "keywords": 1 });
db.processed_posts.createIndex({ "sentiment_confidence": -1 });

// Создание индексов для labeled_posts
db.labeled_posts.createIndex({ "text": "text" });
db.labeled_posts.createIndex({ "sentiment": 1 });

// Вставка тестовых размеченных данных
db.labeled_posts.insertMany([
    {
        text: "Отличный продукт! Очень доволен покупкой, рекомендую всем!",
        sentiment: "positive",
        created_at: new Date()
    },
    {
        text: "Ужасное качество, не рекомендую. Потратил деньги впустую.",
        sentiment: "negative",
        created_at: new Date()
    },
    {
        text: "Обычный товар, ничего особенного. Средний уровень качества.",
        sentiment: "neutral",
        created_at: new Date()
    }
]);

print("MongoDB инициализация завершена успешно!");