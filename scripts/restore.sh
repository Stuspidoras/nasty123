#!/bin/bash

# Скрипт для восстановления из резервной копии

set -e

if [ -z "$1" ]; then
    echo "Использование: ./restore.sh <путь_к_архиву>"
    exit 1
fi

BACKUP_ARCHIVE=$1
TEMP_DIR="./temp_restore"

echo "=== Восстановление из резервной копии ==="

# Распаковка
echo "Распаковка архива..."
mkdir -p $TEMP_DIR
tar -xzf $BACKUP_ARCHIVE -C $TEMP_DIR

# Восстановление PostgreSQL
echo "Восстановление PostgreSQL..."
cat $TEMP_DIR/*/postgres_backup.sql | docker exec -i reviewsdb psql -U postgres reviewsdb

# Восстановление MongoDB
echo "Восстановление MongoDB..."
docker cp $TEMP_DIR/*/mongo_backup reviewsmongo:/tmp/
docker exec reviewsmongo mongorestore /tmp/mongo_backup

# Очистка
rm -rf $TEMP_DIR

echo "✓ Восстановление завершено успешно!"