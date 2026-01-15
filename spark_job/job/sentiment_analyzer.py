import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict
import logging
import spacy
import nltk
from nltk.corpus import stopwords
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Анализатор тональности текста с использованием ML моделей
    """

    def __init__(self, model_path=None):
        # Загрузка предобученной модели для русского языка
        # Используем модель RuBERT для анализа тональности
        model_name = "blanchefort/rubert-base-cased-sentiment"

        try:
            if model_path:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(self.device)
            self.model.eval()

            logger.info(f"Модель загружена на устройство: {self.device}")

        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            raise

        # Загрузка spaCy для обработки текста
        try:
            self.nlp = spacy.load("ru_core_news_sm")
        except:
            logger.warning("Модель spaCy не найдена, используется базовая обработка")
            self.nlp = None

        # Загрузка стоп-слов
        try:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('russian'))
        except:
            self.stop_words = set()

    def preprocess_text(self, text: str) -> str:
        """
        Предобработка текста
        """
        if not text:
            return ""

        # Удаление URL
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Удаление упоминаний и хэштегов
        text = re.sub(r'@\w+|#\w+', '', text)

        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text).strip()

        # Приведение к нижнему регистру
        text = text.lower()

        return text

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Анализ тональности одного текста

        Returns:
            dict: {
                'sentiment': 'positive'|'negative'|'neutral',
                'confidence': float,
                'scores': {'positive': float, 'negative': float, 'neutral': float}
            }
        """
        # Предобработка
        processed_text = self.preprocess_text(text)

        if not processed_text:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            }

        try:
            # Токенизация
            inputs = self.tokenizer(
                processed_text,
                return_tensors='pt',
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)

            # Предсказание
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Преобразование в numpy
            scores = predictions.cpu().numpy()[0]

            # Маппинг для модели blanchefort/rubert-base-cased-sentiment
            # 0: negative, 1: neutral, 2: positive
            sentiment_map = {
                0: 'negative',
                1: 'neutral',
                2: 'positive'
            }

            predicted_class = np.argmax(scores)
            sentiment = sentiment_map[predicted_class]
            confidence = float(scores[predicted_class])

            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'negative': float(scores[0]),
                    'neutral': float(scores[1]),
                    'positive': float(scores[2])
                }
            }

        except Exception as e:
            logger.error(f"Ошибка анализа тональности: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            }

    def batch_analyze(self, texts: List[str], batch_size: int = 32) -> List[Dict]:
        """
        Пакетный анализ тональности
        """
        results = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Предобработка батча
            processed_batch = [self.preprocess_text(text) for text in batch_texts]

            try:
                # Токенизация батча
                inputs = self.tokenizer(
                    processed_batch,
                    return_tensors='pt',
                    truncation=True,
                    max_length=512,
                    padding=True
                ).to(self.device)

                # Предсказание
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

                # Обработка результатов
                scores_batch = predictions.cpu().numpy()

                sentiment_map = {
                    0: 'negative',
                    1: 'neutral',
                    2: 'positive'
                }

                for scores in scores_batch:
                    predicted_class = np.argmax(scores)
                    sentiment = sentiment_map[predicted_class]
                    confidence = float(scores[predicted_class])

                    results.append({
                        'sentiment': sentiment,
                        'confidence': confidence,
                        'scores': {
                            'negative': float(scores[0]),
                            'neutral': float(scores[1]),
                            'positive': float(scores[2])
                        }
                    })

            except Exception as e:
                logger.error(f"Ошибка пакетного анализа: {e}")
                # Добавляем нейтральные результаты для этого батча
                results.extend([{
                    'sentiment': 'neutral',
                    'confidence': 0.0,
                    'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
                }] * len(batch_texts))

        return results

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Извлечение ключевых слов из текста
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)

        # Извлечение существительных и прилагательных
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ', 'VERB'] and
                token.text.lower() not in self.stop_words and
                len(token.text) > 2):
                keywords.append(token.lemma_)

        # Частотный анализ
        from collections import Counter
        keyword_freq = Counter(keywords)

        return [word for word, _ in keyword_freq.most_common(top_n)]

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Извлечение именованных сущностей (NER)
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })

        return entities