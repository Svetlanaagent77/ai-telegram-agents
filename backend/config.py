"""
Конфигурация приложения с поддержкой Voyage AI + DeepSeek
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Основная конфигурация"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN_NTD = os.getenv("TELEGRAM_BOT_TOKEN_NTD")
    TELEGRAM_BOT_TOKEN_DOCS = os.getenv("TELEGRAM_BOT_TOKEN_DOCS")
    
    # AI Provider для генерации (deepseek)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
    AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    
    # DeepSeek настройки
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    # Embeddings - Voyage AI (лучше для русского языка)
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "voyage")  # voyage или openai
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-multilingual-2")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))  # 1024 для Voyage
    
    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "ai-agents-knowledge-base")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/ai_agents")
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RESPONSE_TIME = int(os.getenv("MAX_RESPONSE_TIME", "10"))
    
    # RAG параметры
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
    
    @classmethod
    def get_api_key(cls):
        """Получить API ключ для генерации"""
        if cls.AI_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        elif cls.AI_PROVIDER == "anthropic":
            return cls.ANTHROPIC_API_KEY
        elif cls.AI_PROVIDER == "deepseek":
            return cls.DEEPSEEK_API_KEY
        return None
    
    @classmethod
    def get_embedding_api_key(cls):
        """Получить API ключ для эмбеддингов"""
        if cls.EMBEDDING_PROVIDER == "voyage":
            return cls.VOYAGE_API_KEY
        elif cls.EMBEDDING_PROVIDER == "openai":
            return cls.OPENAI_API_KEY
        return None
    
    @classmethod
    def get_base_url(cls):
        """Получить base URL для API"""
        if cls.AI_PROVIDER == "deepseek":
            return cls.DEEPSEEK_BASE_URL
        return None
    
    @classmethod
    def validate(cls):
        """Проверка обязательных параметров"""
        required = []
        
        if not cls.TELEGRAM_BOT_TOKEN_NTD:
            required.append("TELEGRAM_BOT_TOKEN_NTD")
        if not cls.TELEGRAM_BOT_TOKEN_DOCS:
            required.append("TELEGRAM_BOT_TOKEN_DOCS")
        
        # Проверка API ключей для генерации
        if cls.AI_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY")
        elif cls.AI_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            required.append("ANTHROPIC_API_KEY")
        elif cls.AI_PROVIDER == "deepseek" and not cls.DEEPSEEK_API_KEY:
            required.append("DEEPSEEK_API_KEY")
        
        # Проверка API ключей для эмбеддингов
        if cls.EMBEDDING_PROVIDER == "voyage" and not cls.VOYAGE_API_KEY:
            required.append("VOYAGE_API_KEY")
        elif cls.EMBEDDING_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY (для embeddings)")
        
        if not cls.PINECONE_API_KEY:
            required.append("PINECONE_API_KEY")
        
        if required:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(required)}")
        
        return True
