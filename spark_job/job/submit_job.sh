#!/bin/bash

# Скрипт для запуска Spark задачи

SPARK_MASTER=${SPARK_MASTER:-"spark://spark-master:7077"}
APP_NAME="ReviewAnalytics"
DRIVER_MEMORY="2g"
EXECUTOR_MEMORY="4g"
EXECUTOR_CORES="2"

spark-submit \
  --master $SPARK_MASTER \
  --name $APP_NAME \
  --driver-memory $DRIVER_MEMORY \
  --executor-memory $EXECUTOR_MEMORY \
  --executor-cores $EXECUTOR_CORES \
  --packages org.mongodb.spark:mongo-spark-connector_2.12:10.2.0,org.postgresql:postgresql:42.6.0 \
  --conf spark.mongodb.input.uri="mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}.raw_posts" \
  --conf spark.mongodb.output.uri="mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}.processed_posts" \
  /app/spark_processor.py