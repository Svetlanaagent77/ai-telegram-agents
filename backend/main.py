"""
Главный файл для запуска AI Telegram Agents
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем путь к backend
sys.path.append(str(Path(__file__).parent))

from config import config
from bot.telegram_bot import TelegramAIBot
from rag.rag_engine import RAGEngine


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO if not config.DEBUG else logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )


async def main():
    """Основная функция"""
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   AI TELEGRAM AGENTS - RAG SYSTEM            ║
    ║   Версия 1.0                                  ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Валидация конфигурации
    try:
        config.validate()
        logger.info("✓ Конфигурация проверена")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        logger.error("\nПроверьте файл .env и убедитесь, что все обязательные переменные заданы:")
        logger.error("  - TELEGRAM_BOT_TOKEN_NTD")
        logger.error("  - TELEGRAM_BOT_TOKEN_DOCS")
        logger.error("  - PINECONE_API_KEY")
        logger.error("  - OPENAI_API_KEY или ANTHROPIC_API_KEY")
        return
    
    logger.info(f"AI Provider: {config.AI_PROVIDER}")
    logger.info(f"Model: {config.AI_MODEL}")
    logger.info(f"Pinecone Index НТД: {config.PINECONE_INDEX_NTD}")
    logger.info(f"Pinecone Index Договоры: {config.PINECONE_INDEX_DOCS}")
    
    # Создаем RAG engines для обоих агентов
    logger.info("\n📦 Инициализация RAG engines...")
    
    try:
        # RAG для НТД
        rag_ntd = RAGEngine(
            ai_provider=config.AI_PROVIDER,
            model=config.AI_MODEL
        )
        rag_ntd.initialize_pinecone(
            api_key=config.PINECONE_API_KEY,
            environment=config.PINECONE_ENVIRONMENT,
            index_name=config.PINECONE_INDEX_NTD
        )
        rag_ntd.initialize_embeddings(api_key=config.OPENAI_API_KEY)
        
        # RAG для Договоров
        rag_docs = RAGEngine(
            ai_provider=config.AI_PROVIDER,
            model=config.AI_MODEL
        )
        rag_docs.initialize_pinecone(
            api_key=config.PINECONE_API_KEY,
            environment=config.PINECONE_ENVIRONMENT,
            index_name=config.PINECONE_INDEX_DOCS
        )
        rag_docs.initialize_embeddings(api_key=config.OPENAI_API_KEY)
        
        logger.info("✓ RAG engines инициализированы")
    
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации RAG: {e}")
        return
    
    # Создаем Telegram ботов
    logger.info("\n🤖 Создание Telegram ботов...")
    
    try:
        bot_ntd = TelegramAIBot(
            token=config.TELEGRAM_BOT_TOKEN_NTD,
            agent_name="НТД",
            rag_engine=rag_ntd
        )
        
        bot_docs = TelegramAIBot(
            token=config.TELEGRAM_BOT_TOKEN_DOCS,
            agent_name="Договоры",
            rag_engine=rag_docs
        )
        
        logger.info("✓ Telegram боты созданы")
    
    except Exception as e:
        logger.error(f"❌ Ошибка создания ботов: {e}")
        return
    
    # Запускаем оба бота одновременно
    logger.info("\n🚀 Запуск ботов...\n")
    logger.info("Боты запущены! Нажмите Ctrl+C для остановки.\n")
    
    try:
        await asyncio.gather(
            bot_ntd.start(),
            bot_docs.start()
        )
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Получен сигнал остановки...")
        await bot_ntd.stop()
        await bot_docs.stop()
        logger.info("✓ Боты остановлены")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
