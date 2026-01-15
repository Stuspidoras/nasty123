from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, explode, array, struct
from pyspark.sql.types import StringType, FloatType, StructType, StructField, MapType
from pymongo import MongoClient
import psycopg2
from sentiment_analyzer import SentimentAnalyzer
from config import Config
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SparkProcessor:
    """
    Процессор для параллельной обработки текстов отзывов с использованием Apache Spark
    """

    def __init__(self):
        # Создание Spark сессии
        self.spark = SparkSession.builder \
            .appName(Config.SPARK_APP_NAME) \
            .master(Config.SPARK_MASTER) \
            .config("spark.mongodb.input.uri", f"{Config.get_mongo_url()}/{Config.MONGO_DB}.raw_posts") \
            .config("spark.mongodb.output.uri", f"{Config.get_mongo_url()}/{Config.MONGO_DB}.processed_posts") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.2.0,org.postgresql:postgresql:42.6.0") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.cores", "2") \
            .config("spark.default.parallelism", "8") \
            .getOrCreate()

        # Инициализация анализатора тональности
        self.sentiment_analyzer = SentimentAnalyzer()

        logger.info("Spark сессия создана успешно")

    def load_data_from_mongo(self):
        """
        Загрузка данных из MongoDB
        """
        logger.info("Загрузка данных из MongoDB...")

        df = self.spark.read \
            .format("mongodb") \
            .option("database", Config.MONGO_DB) \
            .option("collection", "raw_posts") \
            .load()

        logger.info(f"Загружено {df.count()} записей")
        return df

    def process_reviews(self):
        """
        Основной процесс обработки отзывов
        """
        # Загрузка данных
        df = self.load_data_from_mongo()

        # Фильтрация пустых текстов
        df = df.filter(col("text").isNotNull() & (col("text") != ""))

        # Регистрация UDF для анализа тональности
        sentiment_schema = StructType([
            StructField("sentiment", StringType(), True),
            StructField("confidence", FloatType(), True),
            StructField("scores", MapType(StringType(), FloatType()), True)
        ])

        def analyze_sentiment_udf(text):
            """UDF для анализа тональности"""
            try:
                result = self.sentiment_analyzer.analyze_sentiment(text)
                return (
                    result['sentiment'],
                    result['confidence'],
                    result['scores']
                )
            except Exception as e:
                logger.error(f"Ошибка в UDF: {e}")
                return ('neutral', 0.0, {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0})

        # Регистрация UDF
        sentiment_udf = udf(analyze_sentiment_udf, sentiment_schema)

        # Применение анализа тональности
        logger.info("Применение анализа тональности...")
        df_processed = df.withColumn("sentiment_analysis", sentiment_udf(col("text")))

        # Разбиение структуры на отдельные колонки
        df_processed = df_processed \
            .withColumn("sentiment", col("sentiment_analysis.sentiment")) \
            .withColumn("sentiment_confidence", col("sentiment_analysis.confidence")) \
            .withColumn("sentiment_scores", col("sentiment_analysis.scores"))

        # Регистрация UDF для извлечения ключевых слов
        keywords_udf = udf(lambda text: self.sentiment_analyzer.extract_keywords(text, top_n=5),
                          ArrayType(StringType()))

        df_processed = df_processed.withColumn("keywords", keywords_udf(col("text")))

        # Регистрация UDF для извлечения сущностей
        entities_schema = ArrayType(StructType([
            StructField("text", StringType(), True),
            StructField("label", StringType(), True)
        ]))

        entities_udf = udf(lambda text: self.sentiment_analyzer.extract_entities(text),
                          entities_schema)

        df_processed = df_processed.withColumn("entities", entities_udf(col("text")))

        # Сохранение в MongoDB
        logger.info("Сохранение обработанных данных в MongoDB...")
        df_processed.write \
            .format("mongodb") \
            .mode("append") \
            .option("database", Config.MONGO_DB) \
            .option("collection", "processed_posts") \
            .save()

        # Сохранение статистики в PostgreSQL
        self.save_statistics_to_postgres(df_processed)

        logger.info("Обработка завершена успешно")

        return df_processed

    def save_statistics_to_postgres(self, df):
        """
        Сохранение статистики в PostgreSQL
        """
        logger.info("Сохранение статистики в PostgreSQL...")

        # Агрегация по тональности
        sentiment_stats = df.groupBy("sentiment", "query", "source").count()

        # Сбор статистики
        stats = sentiment_stats.collect()

        try:
            conn = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD
            )
            cur = conn.cursor()

            for row in stats:
                cur.execute("""
                    INSERT INTO sentiment_statistics 
                    (sentiment, query, source, count, processed_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (query, source, sentiment) 
                    DO UPDATE SET count = sentiment_statistics.count + EXCLUDED.count,
                                 processed_at = NOW()
                """, (row['sentiment'], row['query'], row['source'], row['count']))

            conn.commit()
            cur.close()
            conn.close()

            logger.info("Статистика успешно сохранена в PostgreSQL")

        except Exception as e:
            logger.error(f"Ошибка при сохранении статистики: {e}")

    def get_insights(self, query: str = None):
        """
        Получение аналитики и инсайтов
        """
        logger.info("Генерация аналитики...")

        # Загрузка обработанных данных
        df = self.spark.read \
            .format("mongodb") \
            .option("database", Config.MONGO_DB) \
            .option("collection", "processed_posts") \
            .load()

        if query:
            df = df.filter(col("query") == query)

        # Общая статистика по тональности
        sentiment_distribution = df.groupBy("sentiment").count()

        # Средняя уверенность
        avg_confidence = df.groupBy("sentiment").avg("sentiment_confidence")

        # Топ ключевых слов
        keywords_df = df.select(explode(col("keywords")).alias("keyword"))
        top_keywords = keywords_df.groupBy("keyword").count().orderBy(col("count").desc()).limit(20)

        # Статистика по источникам
        source_stats = df.groupBy("source", "sentiment").count()

        insights = {
            'sentiment_distribution': [row.asDict() for row in sentiment_distribution.collect()],
            'avg_confidence': [row.asDict() for row in avg_confidence.collect()],
            'top_keywords': [row.asDict() for row in top_keywords.collect()],
            'source_statistics': [row.asDict() for row in source_stats.collect()]
        }

        logger.info("Аналитика сгенерирована")

        return insights

    def stop(self):
        """
        Остановка Spark сессии
        """
        self.spark.stop()
        logger.info("Spark сессия остановлена")

if __name__ == "__main__":
    processor = SparkProcessor()

    try:
        # Обработка отзывов
        df_processed = processor.process_reviews()

        # Получение аналитики
        insights = processor.get_insights()

        # Вывод результатов
        print("\n=== АНАЛИТИКА ===")
        print(json.dumps(insights, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Ошибка в процессе обработки: {e}")
    finally:
        processor.stop()