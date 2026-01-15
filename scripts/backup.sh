#!/bin/bash

# Скрипт для резервного копирования данных

set -e

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "=== Резервное копирование ==="

# Backup PostgreSQL
echo "Создание резервной копии PostgreSQL..."
docker exec reviewsdb pg_dump -U postgres reviewsdb > $BACKUP_DIR/postgres_backup.sql

# Backup MongoDB
echo "Создание резервной копии MongoDB..."
docker exec reviewsmongo mongodump --out=/tmp/mongo_backup
docker cp reviewsmongo:/tmp/mongo_backup $BACKUP_DIR/mongo_backup

# Архивация
echo "Создание архива..."
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "✓ Резервная копия создана: $BACKUP_DIR.tar.gz"