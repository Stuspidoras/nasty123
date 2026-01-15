#!/bin/bash

# Скрипт для мониторинга состояния сервисов

while true; do
    clear
    echo "=== Мониторинг VK Review Analytics ==="
    echo "Время: $(date)"
    echo ""

    echo "--- Docker контейнеры ---"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    echo "--- Использование ресурсов ---"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo ""

    echo "--- Логи (последние 5 строк каждого сервиса) ---"
    for service in auth-service collector-service api-service; do
        echo "[$service]"
        docker logs --tail 5 $service 2>&1 | tail -5
        echo ""
    done

    sleep 10
done