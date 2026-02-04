"""
Конфигурация приложения с поддержкой Voyage AI + DeepSeek
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Основная конфигурация - переменные читаются в runtime"""

    # Telegram
    @property
    def TELEGRAM_BOT_TOKEN(self):
        return os.getenv("TELEGRAM_BOT_TOKEN")

    @property
    def AGENT_TYPE(self):
        return os.getenv("AGENT_TYPE")

    # AI Provider для генерации (deepseek)
    @property
    def AI_PROVIDER(self):
        return os.getenv("AI_PROVIDER", "deepseek")

    @property
    def AI_MODEL(self):
        return os.getenv("AI_MODEL", "deepseek-chat")

    # API Keys
    @property
    def OPENAI_API_KEY(self):
        return os.getenv("OPENAI_API_KEY")

    @property
    def ANTHROPIC_API_KEY(self):
        return os.getenv("ANTHROPIC_API_KEY")

    @property
    def DEEPSEEK_API_KEY(self):
        return os.getenv("DEEPSEEK_API_KEY")

    @property
    def VOYAGE_API_KEY(self):
        return os.getenv("VOYAGE_API_KEY")

    # DeepSeek настройки
    @property
    def DEEPSEEK_BASE_URL(self):
        return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")  # ✅ УБРАНЫ ПРОБЕЛЫ!

    # Embeddings - Voyage AI (лучше для русского языка)
    @property
    def EMBEDDING_PROVIDER(self):
        return os.getenv("EMBEDDING_PROVIDER", "voyage")

    @property
    def EMBEDDING_MODEL(self):
        return os.getenv("EMBEDDING_MODEL", "voyage-multilingual-2")

    @property
    def EMBEDDING_DIMENSION(self):
        return int(os.getenv("EMBEDDING_DIMENSION", "1024"))

    # Pinecone
    @property
    def PINECONE_API_KEY(self):
        return os.getenv("PINECONE_API_KEY")

    @property
    def PINECONE_ENVIRONMENT(self):
        return os.getenv("PINECONE_ENVIRONMENT")

    @property
    def PINECONE_INDEX(self):
        return os.getenv("PINECONE_INDEX", "sveta1")

    # Database
    @property
    def DATABASE_URL(self):
        return os.getenv("DATABASE_URL", "postgresql://localhost/ai_agents")

    # Application
    @property
    def DEBUG(self):
        return os.getenv("DEBUG", "False").lower() == "true"

    @property
    def LOG_LEVEL(self):
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def MAX_RESPONSE_TIME(self):
        return int(os.getenv("MAX_RESPONSE_TIME", "10"))

    # RAG параметры
    @property
    def CHUNK_SIZE(self):
        return int(os.getenv("CHUNK_SIZE", "500"))  # ✅ УМЕНЬШЕНО ДО 500

    @property
    def CHUNK_OVERLAP(self):
        return int(os.getenv("CHUNK_OVERLAP", "100"))  # ✅ УВЕЛИЧЕНО ДО 100

    @property
    def TOP_K_RESULTS(self):
        return int(os.getenv("TOP_K_RESULTS", "7"))  # ✅ УВЕЛИЧЕНО ДО 7

    def get_api_key(self):
        """Получить API ключ для генерации"""
        if self.AI_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        elif self.AI_PROVIDER == "anthropic":
            return self.ANTHROPIC_API_KEY
        elif self.AI_PROVIDER == "deepseek":
            return self.DEEPSEEK_API_KEY
        return None

    def get_embedding_api_key(self):
        """Получить API ключ для эмбеддингов"""
        if self.EMBEDDING_PROVIDER == "voyage":
            return self.VOYAGE_API_KEY
        elif self.EMBEDDING_PROVIDER == "openai":
            return self.OPENAI_API_KEY
        return None

    def get_base_url(self):
        """Получить base URL для API"""
        if self.AI_PROVIDER == "deepseek":
            return self.DEEPSEEK_BASE_URL.strip()  # ✅ ДОБАВЛЕН .strip()!
        return None

    def validate(self):
        """Проверка обязательных параметров"""
        required = []

        if not self.TELEGRAM_BOT_TOKEN:
            required.append("TELEGRAM_BOT_TOKEN")
        
        if not self.AGENT_TYPE:
            required.append("AGENT_TYPE")

        # Проверка API ключей для генерации
        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY")
        elif self.AI_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            required.append("ANTHROPIC_API_KEY")
        elif self.AI_PROVIDER == "deepseek" and not self.DEEPSEEK_API_KEY:
            required.append("DEEPSEEK_API_KEY")

        # Проверка API ключей для эмбеддингов
        if self.EMBEDDING_PROVIDER == "voyage" and not self.VOYAGE_API_KEY:
            required.append("VOYAGE_API_KEY")
        elif self.EMBEDDING_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY (для embeddings)")

        if not self.PINECONE_API_KEY:
            required.append("PINECONE_API_KEY")

        if required:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(required)}")

        return True


# Singleton instance
config = Config()
