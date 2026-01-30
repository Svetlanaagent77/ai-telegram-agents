cat > main.py << 'EOF'
"""
Main - точка входа для запуска AI Telegram Agent (один бот)
"""
import asyncio
import logging
import os
from pathlib import Path
import sys

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from backend.rag.rag_engine import RAGEngine
from backend.bot.telegram_agent import TelegramAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    # Проверяем обязательные переменные
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    agent_type = os.getenv("AGENT_TYPE")  # "ntd" или "docs"
    
    if not bot_token:
        logger.error("❌ Отсутствует TELEGRAM_BOT_TOKEN")
        return
    
    if not agent_type:
        logger.error("❌ Отсутствует AGENT_TYPE")
        return
    
    # Получаем API ключи
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    voyage_api_key = os.getenv("VOYAGE_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not all([pinecone_api_key, voyage_api_key, deepseek_api_key]):
        logger.error("❌ Отсутствуют API ключи")
        return
    
    # Инициализируем RAG
    rag_engine = RAGEngine(
        api_key=deepseek_api_key,
        pinecone_api_key=pinecone_api_key,
        index_name="sveta-agent",
        agent_type=agent_type,
        voyage_api_key=voyage_api_key,
        embedding_provider="voyage"
    )
    rag_engine.init_index()
    
    # Запускаем бота
    agent_name = "Агент НТД" if agent_type == "ntd" else "Агент Договоры"
    bot = TelegramAgent(bot_token, rag_engine, agent_name)
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
EOF
