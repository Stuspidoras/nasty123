#!/bin/bash

# Скрипт для запуска тестов

set -e

echo "=== Запуск тестов VK Review Analytics ==="

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Функция для запуска тестов сервиса
run_service_tests() {
    local service=$1
    echo -e "${GREEN}Тестирование ${service}...${NC}"

    cd ${service}

    if [ -f "requirements.txt" ]; then
        # Python тесты
        pip install -q pytest pytest-cov
        pytest tests/ --cov=${service} --cov-report=html --cov-report=term
    elif [ -f "package.json" ]; then
        # JavaScript тесты
        npm test -- --coverage
    fi

    cd ..
}

# Тестирование Auth Service
run_service_tests "auth"

# Тестирование Collector Service
run_service_tests "collector"

# Тестирование API Service
run_service_tests "api"

# Тестирование Frontend
run_service_tests "frontend"

echo -e "${GREEN}✓ Все тесты пройдены успешно!${NC}"