"""
RAG Engine - система поиска по векторным базам знаний
Поддержка: Voyage AI (embeddings) + DeepSeek (генерация)
"""
from typing import List, Dict, Optional
import logging
import httpx
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoyageEmbeddings:
    """Клиент для Voyage AI Embeddings"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "voyage-multilingual-2"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.voyageai.com/v1"  # ✅ ИСПРАВЛЕНО: убраны пробелы в конце!
    
    def embed(self, text: str, input_type: str = "document") -> List[float]:
        """Получить эмбеддинг для одного текста"""
        return self.embed_batch([text], input_type)[0]
    
    def embed_query(self, text: str) -> List[float]:
        """Эмбеддинг для поискового запроса"""
        return self.embed(text, input_type="query")
    
    def embed_batch(self, texts: List[str], input_type: str = "document") -> List[List[float]]:
        """Получить эмбеддинги для списка текстов"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts,
            "input_type": input_type
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
        
        # Сортируем по индексу
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in sorted_data]


class RAGEngine:
    """Система RAG для поиска и генерации ответов с поддержкой фильтров"""
    
    def __init__(
        self,
        api_key: str,
        pinecone_api_key: str,
        index_name: str,
        agent_type: str = None,  # 'ntd' или 'docs'
        embedding_model: str = "voyage-multilingual-2",
        embedding_dimension: int = 1024,
        top_k: int = 3,
        base_url: str = None,
        ai_provider: str = "deepseek",
        voyage_api_key: str = None,
        embedding_provider: str = "voyage"
    ):
        """
        Args:
            api_key: ключ API для генерации (DeepSeek)
            pinecone_api_key: ключ Pinecone API
            index_name: название индекса в Pinecone
            agent_type: тип агента для фильтрации ('ntd' или 'docs')
            embedding_model: модель для embeddings
            embedding_dimension: размерность векторов (1024 для Voyage)
            top_k: количество результатов поиска
            base_url: базовый URL API (для DeepSeek)
            ai_provider: провайдер AI для генерации (deepseek)
            voyage_api_key: ключ Voyage AI для эмбеддингов
            embedding_provider: провайдер эмбеддингов (voyage или openai)
        """
        self.api_key = api_key
        self.pinecone_api_key = pinecone_api_key
        self.embedding_model = embedding_model
        self.embedding_dimension = embedding_dimension
        self.top_k = top_k
        self.index_name = index_name
        self.base_url = base_url
        self.ai_provider = ai_provider
        self.agent_type = agent_type
        self.embedding_provider = embedding_provider
        self.voyage_api_key = voyage_api_key
        
        # Инициализация Voyage клиента
        if embedding_provider == "voyage" and voyage_api_key:
            self.voyage_client = VoyageEmbeddings(
                api_key=voyage_api_key,
                model=embedding_model
            )
            logger.info(f"✅ Voyage AI инициализирован: {embedding_model}")
        else:
            self.voyage_client = None
        
        # Будет инициализирован при подключении
        self.index = None
    
    def create_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """
        Создание embedding для текста
        
        Args:
            text: входной текст
            is_query: True если это поисковый запрос
            
        Returns:
            вектор embedding
        """
        # Voyage AI
        if self.embedding_provider == "voyage" and self.voyage_client:
            try:
                if is_query:
                    return self.voyage_client.embed_query(text)
                else:
                    return self.voyage_client.embed(text)
            except Exception as e:
                logger.error(f"Ошибка Voyage AI: {e}")
                raise
        
        # Fallback на OpenAI
        import openai
        
        if self.base_url:
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            client = openai.OpenAI(api_key=self.api_key)
        
        try:
            response = client.embeddings.create(input=text, model=self.embedding_model)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Ошибка при создании embedding: {e}")
            raise
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Семантический поиск по базе знаний с фильтрацией по типу агента
        
        Args:
            query: поисковый запрос
            top_k: количество результатов
            
        Returns:
            список найденных документов
        """
        if not self.index:
            logger.error("Индекс не инициализирован")
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Создаем embedding для запроса (is_query=True для Voyage)
            query_embedding = self.create_embedding(query, is_query=True)
            
            # Формируем фильтр по типу агента
            search_filter = None
            if self.agent_type:
                search_filter = {"agent_type": self.agent_type}
                logger.info(f"Поиск с фильтром: {search_filter}")
            
            # Ищем похожие векторы с фильтром
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=search_filter  # Фильтр по типу агента!
            )
            
            # Форматируем результаты
            documents = []
            for match in results['matches']:
                documents.append({
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('text', ''),
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'text'}
                })
            
            return documents
        
        except Exception as e:
            logger.error(f"Ошибка при поиске: {e}")
            return []
    
    def delete_documents_by_filename(self, filename: str) -> bool:
        """
        Удаление всех чанков документа по имени файла
        
        Args:
            filename: имя файла для удаления
            
        Returns:
            успешность удаления
        """
        if not self.index:
            logger.error("Индекс не инициализирован")
            return False
        
        try:
            # Формируем фильтр
            delete_filter = {"filename": filename}
            if self.agent_type:
                delete_filter["agent_type"] = self.agent_type
            
            # Удаляем по фильтру
            self.index.delete(filter=delete_filter)
            
            logger.info(f"✅ Удалены все чанки документа: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Ошибка при удалении: {e}")
            return False
    
    def list_documents(self) -> List[str]:
        """
        Получение списка всех документов агента
        
        Returns:
            список имён файлов
        """
        if not self.index:
            logger.error("Индекс не инициализирован")
            return []
        
        try:
            # Получаем статистику индекса
            stats = self.index.describe_index_stats()
            
            # В Pinecone нет прямого способа получить список уникальных метаданных
            # Возвращаем информацию о количестве векторов
            namespaces = stats.get('namespaces', {})
            
            logger.info(f"📊 Статистика индекса: {stats}")
            
            return []  # Pinecone не поддерживает список документов напрямую
        
        except Exception as e:
            logger.error(f"❌ Ошибка при получении списка: {e}")
            return []
    
    def init_index(self, pinecone_api_key: str = None):
        """Инициализация индекса Pinecone"""
        from pinecone import Pinecone
        
        api_key = pinecone_api_key or self.pinecone_api_key
        pc = Pinecone(api_key=api_key)
        self.index = pc.Index(self.index_name)
        logger.info(f"✅ Pinecone индекс подключен: {self.index_name}")
    
    def add_documents(self, documents: List[Dict], batch_size: int = 100):
        """
        Добавление документов в векторную базу
        Использует батчинг эмбеддингов для обхода rate limit
        
        Args:
            documents: список документов [{id, text, metadata}, ...]
            batch_size: размер батча для загрузки
        """
        from pinecone import Pinecone
        
        # Инициализация Pinecone если не было
        if not self.index:
            pc = Pinecone(api_key=self.pinecone_api_key)
            self.index = pc.Index(self.index_name)
        
        # Собираем все тексты для батч-эмбеддинга
        texts = [doc['text'] for doc in documents]
        
        # Получаем все эмбеддинги ОДНИМ запросом (батч)
        logger.info(f"📊 Создание эмбеддингов для {len(texts)} чанков одним запросом...")
        
        # ✅ ИСПРАВЛЕНО: было self.voyage_embeddings → стало self.voyage_client
        if self.embedding_provider == "voyage" and self.voyage_client:
            embeddings = self.voyage_client.embed_batch(texts, input_type="document")
        else:
            # Fallback - по одному (для OpenAI)
            embeddings = []
            for text in texts:
                emb = self.create_embedding(text, is_query=False)
                embeddings.append(emb)
                time.sleep(0.5)
        
        # Формируем векторы
        vectors = []
        for i, doc in enumerate(documents):
            vectors.append({
                'id': doc['id'],
                'values': embeddings[i],
                'metadata': {
                    'text': doc['text'][:8000],  # Лимит Pinecone
                    **doc.get('metadata', {})
                }
            })
        
        # Загружаем в Pinecone батчами
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
            logger.info(f"📤 Загружено {len(batch)} векторов")
        
        logger.info(f"✅ Всего добавлено {len(documents)} документов")

    def generate_answer(
        self,
        query: str,
        context_documents: List[Dict],
        model: str = "deepseek-chat",
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Генерация ответа на основе найденных документов
        """
        import openai
        
        # Настройка клиента
        if self.base_url:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            client = openai.OpenAI(api_key=self.api_key)
        
        # Формируем контекст
        context = "\n\n".join([
            f"Документ {i+1}:\n{doc['text']}"
            for i, doc in enumerate(context_documents)
        ])
        
        if system_prompt is None:
            system_prompt = """Ты - AI-ассистент для поиска информации в документах.
Отвечай только на основе предоставленных документов, кратко и по существу.
Если информации нет в документах - так и скажи."""
        
        user_prompt = f"""Контекст из документов:
{context}

Вопрос пользователя: {query}

Ответ:"""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Ошибка при генерации: {e}")
            return "Ошибка при генерации ответа."


if __name__ == "__main__":
    print("RAG Engine модуль готов!")
