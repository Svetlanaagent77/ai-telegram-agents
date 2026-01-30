"""
Main - точка входа для запуска AI Telegram Agent (один бот)
"""
import asyncio
import logging
import os
from pathlib import Path
import sys

# Добавляем путь к корню проекта (только один уровень)
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.rag_engine import RAGEngine
from backend.bot.telegram_agent import TelegramAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    agent_type = os.getenv("AGENT_TYPE")
    
    if not bot_token or not agent_type:
        logger.error("❌ Отсутствуют TELEGRAM_BOT_TOKEN или AGENT_TYPE")
        return
    
    rag = RAGEngine(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        index_name="sveta-agent",
        agent_type=agent_type,
        voyage_api_key=os.getenv("VOYAGE_API_KEY"),
        embedding_provider="voyage"
    )
    rag.init_index()
    
    name = "Агент НТД" if agent_type == "ntd" else "Агент Договоры"
    bot = TelegramAgent(bot_token, rag, name)
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
