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
        return os.getenv("AGENT_TYPE", "docs")  # дефолт — docs (для safety)

    # AI Provider
    @property
    def AI_PROVIDER(self):
        return os.getenv("AI_PROVIDER", "deepseek")

    @property
    def AI_MODEL(self):
        return os.getenv("AI_MODEL", "deepseek-chat")

    # API Keys
    @property
    def DEEPSEEK_API_KEY(self):
        return os.getenv("DEEPSEEK_API_KEY")

    @property
    def VOYAGE_API_KEY(self):
        return os.getenv("VOYAGE_API_KEY")

    # DeepSeek URL — без пробелов!
    @property
    def DEEPSEEK_BASE_URL(self):
        return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # Embeddings
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
    def PINECONE_INDEX(self):
        return os.getenv("PINECONE_INDEX", "sveta1")

    # RAG параметры
    @property
    def CHUNK_SIZE(self):
        return int(os.getenv("CHUNK_SIZE", "500"))

    @property
    def CHUNK_OVERLAP(self):
        return int(os.getenv("CHUNK_OVERLAP", "100"))

    @property
    def TOP_K_RESULTS(self):
        return int(os.getenv("TOP_K_RESULTS", "7"))

    def get_api_key(self):
        return self.DEEPSEEK_API_KEY

    def get_embedding_api_key(self):
        return self.VOYAGE_API_KEY

    def get_base_url(self):
        return self.DEEPSEEK_BASE_URL.strip()

    def validate(self):
        required = []
        if not self.TELEGRAM_BOT_TOKEN:
            required.append("TELEGRAM_BOT_TOKEN")
        if not self.AGENT_TYPE:
            required.append("AGENT_TYPE")
        if not self.DEEPSEEK_API_KEY:
            required.append("DEEPSEEK_API_KEY")
        if not self.VOYAGE_API_KEY:
            required.append("VOYAGE_API_KEY")
        if not self.PINECONE_API_KEY:
            required.append("PINECONE_API_KEY")

        if required:
            raise ValueError(f"Отсутствуют обязательные переменные: {', '.join(required)}")
        return True


config = Config()
