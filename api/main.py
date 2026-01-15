from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collector.vk_collector import VKCollector
from collector.ok_collector import OKCollector
from database.postgres_handler import PostgresHandler
from database.mongo_handler import MongoHandler
import uuid
import subprocess

app = FastAPI(title="Social Media Review Analytics API", version="1.0.0")

# Инициализация
vk_collector = VKCollector()
ok_collector = OKCollector()
postgres_db = PostgresHandler()
mongo_db = MongoHandler()

class SearchRequest(BaseModel):
    keywords: List[str]
    brand: Optional[str] = None
    sources: List[str] = ["vk", "ok"]
    max_posts: int = 1000
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_reviews(request: SearchRequest, background_tasks: BackgroundTasks):
    """Запуск анализа отзывов"""
    job_id = str(uuid.uuid4())

    postgres_db.create_job(
        job_id=job_id,
        keywords=request.keywords,
        brand=request.brand,
        sources=request.sources,
        status="pending"
    )

    background_tasks.add_task(collect_and_analyze, job_id, request)

    return AnalysisResponse(
        job_id=job_id,
        status="pending",
        message="Анализ запущен. Используйте job_id для проверки статуса."
    )

async def collect_and_analyze(job_id: str, request: SearchRequest):
    """Сбор данных и запуск анализа"""
    try:
        postgres_db.update_job_status(job_id, "collecting")

        all_posts = []

        if "vk" in request.sources:
            vk_posts = await vk_collector.collect_posts(
                keywords=request.keywords,
                brand=request.brand,
                max_posts=request.max_posts,
                date_from=request.date_from,
                date_to=request.date_to
            )
            all_posts.extend(vk_posts)

        if "ok" in request.sources:
            ok_posts = await ok_collector.collect_posts(
                keywords=request.keywords,
                brand=request.brand,
                max_posts=request.max_posts,
                date_from=request.date_from,
                date_to=request.date_to
            )
            all_posts.extend(ok_posts)

        mongo_db.save_raw_posts(job_id, all_posts)
        postgres_db.update_job_status(job_id, "processing")
        postgres_db.update_posts_count(job_id, len(all_posts))

        # Запуск Spark Job
        spark_submit_cmd = [
            "spark-submit",
            "--master", "spark://spark-master:7077",
            "--deploy-mode", "client",
            "--packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
            "/app/spark_job/job/sentiment_analysis.py",
            job_id
        ]
        subprocess.run(spark_submit_cmd, check=True)

        postgres_db.update_job_status(job_id, "completed")

    except Exception as e:
        postgres_db.update_job_status(job_id, "failed")
        postgres_db.update_job_error(job_id, str(e))

@app.get("/api/v1/job/{job_id}")
async def get_job_status(job_id: str):
    """Получить статус задачи"""
    job = postgres_db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/v1/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Получить результаты анализа"""
    results = mongo_db.get_analysis_results(job_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    return results

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)