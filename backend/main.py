"""
Главный файл для запуска AI Telegram Agent (один бот на сервис)
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем путь к backend
sys.path.append(str(Path(__file__).parent))

from backend.bot.telegram_agent import TelegramAgent
from backend.rag.rag_engine import RAGEngine


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


async def main():
    """Основная функция для одного бота"""
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   AI TELEGRAM AGENT - RAG SYSTEM              ║
    ║   Версия 2.0 (Single Bot)                     ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Получаем обязательные переменные
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    agent_type = os.getenv("AGENT_TYPE")  # "ntd" или "docs"
    
    if not bot_token:
        logger.error("❌ Отсутствует TELEGRAM_BOT_TOKEN")
        return
    
    if not agent_type:
        logger.error("❌ Отсутствует AGENT_TYPE (ntd/docs)")
        return
    
    # Настройки из переменных окружения
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    voyage_api_key = os.getenv("VOYAGE_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "sveta-agent")
    
    # Валидация
    if not all([pinecone_api_key, voyage_api_key, deepseek_api_key]):
        logger.error("❌ Отсутствуют обязательные API ключи")
        return
    
    logger.info(f"🤖 Запуск бота для agent_type: {agent_type}")
    
    try:
        # Инициализация RAG Engine
        rag_engine = RAGEngine(
            api_key=deepseek_api_key,
            pinecone_api_key=pinecone_api_key,
            index_name=index_name,
            agent_type=agent_type,
            voyage_api_key=voyage_api_key,
            embedding_provider="voyage"
        )
        rag_engine.init_index()
        logger.info("✅ RAG Engine инициализирован")
        
        # Создание и запуск бота
        agent_name = "Агент НТД" if agent_type == "ntd" else "Агент Договоры"
        telegram_agent = TelegramAgent(
            bot_token=bot_token,
            rag_engine=rag_engine,
            agent_name=agent_name
        )
        
        logger.info(f"🚀 Запуск {agent_name}...")
        await telegram_agent.start()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
