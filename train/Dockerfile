FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скачивание моделей и данных
RUN python -m spacy download ru_core_news_sm
RUN python -m nltk.downloader stopwords punkt

COPY . .

CMD ["python", "train_model.py"]