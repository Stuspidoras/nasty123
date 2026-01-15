#!/bin/bash

# Скрипт для развертывания проекта

set -e

echo "=== Развертывание VK Review Analytics ==="

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка необходимых инструментов
check_requirements() {
    log_info "Проверка необходимых инструментов..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен!"
        exit 1
    fi

    if ! command -v kubectl &> /dev/null; then
        log_warn "kubectl не установлен. Развертывание в Kubernetes будет недоступно."
    fi

    log_info "✓ Все необходимые инструменты установлены"
}

# Docker Compose развертывание
deploy_docker_compose() {
    log_info "Запуск развертывания через Docker Compose..."

    cd infra

    # Проверка .env файла
    if [ ! -f ../.env ]; then
        log_warn ".env файл не найден, создание из .env.example..."
        cp ../.env.example ../.env
        log_warn "Пожалуйста, заполните переменные окружения в .env файле"
        exit 1
    fi

    # Сборка образов
    log_info "Сборка Docker образов..."
    docker-compose build

    # Запуск контейнеров
    log_info "Запуск контейнеров..."
    docker-compose up -d

    # Проверка статуса
    log_info "Проверка статуса контейнеров..."
    sleep 10
    docker-compose ps

    log_info "✓ Docker Compose развертывание завершено"
    log_info "Доступ к сервисам:"
    log_info "  - Frontend: http://localhost:3000"
    log_info "  - API: http://localhost:5002"
    log_info "  - Auth: http://localhost:5000"
    log_info "  - Collector: http://localhost:5001"
    log_info "  - Spark Master UI: http://localhost:8080"
}

# Kubernetes развертывание
deploy_kubernetes() {
    log_info "Запуск развертывания в Kubernetes..."

    cd infra/kubernetes

    # Создание namespace
    log_info "Создание namespace..."
    kubectl apply -f namespace.yaml

    # Развертывание баз данных
    log_info "Развертывание PostgreSQL..."
    kubectl apply -f postgres-deployment.yaml

    log_info "Развертывание MongoDB..."
    kubectl apply -f mongo-deployment.yaml

    log_info "Развертывание Redis..."
    kubectl apply -f redis-deployment.yaml

    # Ожидание готовности БД
    log_info "Ожидание готовности баз данных..."
    kubectl wait --for=condition=ready pod -l app=postgres -n review-analytics --timeout=300s
    kubectl wait --for=condition=ready pod -l app=mongodb -n review-analytics --timeout=300s

    # Развертывание Spark
    log_info "Развертывание Spark Master..."
    kubectl apply -f spark-master-deployment.yaml

    log_info "Развертывание Spark Workers..."
    kubectl apply -f spark-worker-deployment.yaml

    # Развертывание сервисов
    log_info "Развертывание Auth Service..."
    kubectl apply -f auth-deployment.yaml

    log_info "Развертывание Collector Service..."
    kubectl apply -f collector-deployment.yaml

    log_info "Развертывание API Service..."
    kubectl apply -f api-deployment.yaml

    log_info "Развертывание Frontend..."
    kubectl apply -f frontend-deployment.yaml

    # Развертывание Ingress
    log_info "Развертывание Ingress..."
    kubectl apply -f ingress.yaml

    # Проверка статуса
    log_info "Проверка статуса подов..."
    kubectl get pods -n review-analytics

    log_info "✓ Kubernetes развертывание завершено"
    log_info "Для доступа к сервисам выполните:"
    log_info "  kubectl port-forward -n review-analytics svc/frontend 3000:80"
}

# Остановка сервисов
stop_services() {
    log_info "Остановка сервисов..."

    if [ "$1" == "docker" ]; then
        cd infra
        docker-compose down
        log_info "✓ Docker Compose сервисы остановлены"
    elif [ "$1" == "k8s" ]; then
        kubectl delete namespace review-analytics
        log_info "✓ Kubernetes сервисы остановлены"
    fi
}

# Главное меню
main() {
    check_requirements

    echo ""
    echo "Выберите режим развертывания:"
    echo "1) Docker Compose (рекомендуется для разработки)"
    echo "2) Kubernetes (для продакшена)"
    echo "3) Остановить Docker Compose"
    echo "4) Остановить Kubernetes"
    echo "5) Выход"
    echo ""

    read -p "Ваш выбор: " choice

    case $choice in
        1)
            deploy_docker_compose
            ;;
        2)
            deploy_kubernetes
            ;;
        3)
            stop_services "docker"
            ;;
        4)
            stop_services "k8s"
            ;;
        5)
            log_info "Выход"
            exit 0
            ;;
        *)
            log_error "Неверный выбор"
            exit 1
            ;;
    esac
}

# Запуск
main