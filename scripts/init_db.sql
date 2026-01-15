-- Создание базы данных и таблиц для PostgreSQL

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица собранных постов (метаданные)
CREATE TABLE IF NOT EXISTS collected_posts (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    post_id VARCHAR(255) NOT NULL,
    text TEXT,
    date TIMESTAMP,
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    query VARCHAR(255),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, post_id)
);

-- Таблица статистики по тональности
CREATE TABLE IF NOT EXISTS sentiment_statistics (
    id SERIAL PRIMARY KEY,
    sentiment VARCHAR(50) NOT NULL,
    query VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,
    count INTEGER DEFAULT 0,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(query, source, sentiment)
);

-- Таблица задач обработки
CREATE TABLE IF NOT EXISTS processing_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    keywords TEXT[],
    sources TEXT[],
    total_collected INTEGER DEFAULT 0,
    total_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX idx_collected_posts_query ON collected_posts(query);
CREATE INDEX idx_collected_posts_source ON collected_posts(source);
CREATE INDEX idx_collected_posts_date ON collected_posts(date);
CREATE INDEX idx_sentiment_statistics_query ON sentiment_statistics(query);
CREATE INDEX idx_processing_tasks_user ON processing_tasks(user_id);
CREATE INDEX idx_processing_tasks_status ON processing_tasks(status);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Вставка тестового пользователя (пароль: test123)
INSERT INTO users (username, email, password_hash)
VALUES ('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIBz8qRvSu')
ON CONFLICT (email) DO NOTHING;

COMMENT ON TABLE users IS 'Таблица пользователей системы';
COMMENT ON TABLE collected_posts IS 'Метаданные собранных постов';
COMMENT ON TABLE sentiment_statistics IS 'Агрегированная статистика по тональности';
COMMENT ON TABLE processing_tasks IS 'Задачи обработки данных';