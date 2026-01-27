"""
Main - точка входа для запуска AI Telegram Agents
"""
import asyncio
import logging
from pathlib import Path
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import config
from backend.rag.rag_engine import RAGEngine
from backend.bot.telegram_agent import TelegramAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска системы"""
    
    logger.info("="*60)
    logger.info("AI Telegram Agents - Запуск системы")
    logger.info("="*60)
    
    # Проверка конфигурации
    try:
        config.validate()
        logger.info("✅ Конфигурация проверена")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        logger.info("\n📝 Создайте .env файл с необходимыми параметрами:")
        logger.info("   cp .env.example .env")
        logger.info("   nano .env")
        return
    
    # Инициализация RAG для агента НТД
    logger.info("\n🔧 Инициализация RAG для Агента #1 (НТД)...")
    try:
        rag_ntd = RAGEngine(
            api_key=config.get_api_key(),
            pinecone_api_key=config.PINECONE_API_KEY,
            index_name=config.PINECONE_INDEX,
            agent_type='ntd',
            embedding_model=config.EMBEDDING_MODEL,
            embedding_dimension=config.EMBEDDING_DIMENSION,
            top_k=config.TOP_K_RESULTS,
            base_url=config.get_base_url(),
            ai_provider=config.AI_PROVIDER,
            voyage_api_key=config.VOYAGE_API_KEY,
            embedding_provider=config.EMBEDDING_PROVIDER
        )
        logger.info(f"✅ RAG для НТД готов (embeddings: {config.EMBEDDING_PROVIDER})")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации RAG НТД: {e}")
        rag_ntd = None
    
    # Инициализация RAG для агента Договоры
    logger.info("\n🔧 Инициализация RAG для Агента #2 (Договоры)...")
    try:
        rag_docs = RAGEngine(
            api_key=config.get_api_key(),
            pinecone_api_key=config.PINECONE_API_KEY,
            index_name=config.PINECONE_INDEX,
            agent_type='docs',
            embedding_model=config.EMBEDDING_MODEL,
            embedding_dimension=config.EMBEDDING_DIMENSION,
            top_k=config.TOP_K_RESULTS,
            base_url=config.get_base_url(),
            ai_provider=config.AI_PROVIDER,
            voyage_api_key=config.VOYAGE_API_KEY,
            embedding_provider=config.EMBEDDING_PROVIDER
        )
        logger.info(f"✅ RAG для Договоров готов (embeddings: {config.EMBEDDING_PROVIDER})")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации RAG Договоры: {e}")
        rag_docs = None
    
    # Создание ботов
    logger.info("\n🤖 Создание Telegram ботов...")
    
    bot_ntd = TelegramAgent(
        bot_token=config.TELEGRAM_BOT_TOKEN_NTD,
        rag_engine=rag_ntd,
        agent_name="Агент НТД"
    )
    logger.info("✅ Бот НТД создан")
    
    bot_docs = TelegramAgent(
        bot_token=config.TELEGRAM_BOT_TOKEN_DOCS,
        rag_engine=rag_docs,
        agent_name="Агент Договоры"
    )
    logger.info("✅ Бот Договоры создан")
    
    # Запуск ботов параллельно
    logger.info("\n🚀 Запуск ботов...")
    logger.info("="*60)
    
    try:
        await asyncio.gather(
            bot_ntd.start(),
            bot_docs.start()
        )
    except KeyboardInterrupt:
        logger.info("\n⏹ Остановка системы...")
    except Exception as e:
        logger.error(f"\n❌ Ошибка при работе: {e}")
    finally:
        logger.info("👋 Система остановлена")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 До свидания!")
