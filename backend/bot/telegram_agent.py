"""
Telegram Bot - обработчики сообщений
"""
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramAgent:
    """Telegram бот-агент для обработки запросов"""
    
    def __init__(self, bot_token: str, rag_engine, agent_name: str = "Агент"):
        """
        Args:
            bot_token: токен бота
            rag_engine: экземпляр RAGEngine
            agent_name: название агента (для логов)
        """
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.rag_engine = rag_engine
        self.agent_name = agent_name
        
        # Регистрируем обработчики
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            """Обработчик команды /start"""
            welcome_text = f"""
👋 Привет! Я {self.agent_name}.

Я помогу найти информацию в базе знаний.

Просто задай мне вопрос, и я постараюсь найти ответ в документах.

Доступные команды:
/start - это сообщение
/help - справка
"""
            await message.answer(welcome_text)
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            """Обработчик команды /help"""
            help_text = """
📚 Как пользоваться ботом:

1. Задай вопрос обычным текстом
2. Я найду релевантную информацию в документах
3. Сформирую ответ на основе найденного

Примеры вопросов:
• "Какие требования по ГОСТ 12345?"
• "Что говорит СНиП о..."
• "Найди информацию о..."

⏱ Время ответа: обычно до 10 секунд
"""
            await message.answer(help_text)
        
        @self.dp.message(F.text)
        async def handle_question(message: Message):
            """Обработчик текстовых вопросов"""
            user_question = message.text
            
            logger.info(f"{self.agent_name} - Получен вопрос от {message.from_user.id}: {user_question}")
            
            # Отправляем "печатает..."
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action="typing"
            )
            
            try:
                # Поиск в базе знаний
                if self.rag_engine:
                    # Используем RAG для поиска и генерации
                    result = self.rag_engine.query(user_question)
                    
                    answer = result.get('answer', 'Не удалось найти информацию')
                    sources = result.get('sources', [])
                    
                    # Формируем ответ с источниками
                    response = f"{answer}\n\n"
                    
                    if sources:
                        response += "📄 Источники:\n"
                        for i, source in enumerate(sources, 1):
                            score = source.get('score', 0)
                            doc_info = source.get('metadata', {})
                            filename = doc_info.get('filename', f'Документ {i}')
                            response += f"{i}. {filename} (релевантность: {score:.2%})\n"
                else:
                    # Fallback без RAG
                    response = "⚠️ Система поиска временно недоступна. Попробуйте позже."
                
                await message.answer(response)
                logger.info(f"{self.agent_name} - Ответ отправлен")
            
            except Exception as e:
                logger.error(f"{self.agent_name} - Ошибка: {e}")
                await message.answer(
                    "❌ Произошла ошибка при обработке запроса. Попробуйте еще раз."
                )
    
    async def start(self):
        """Запуск бота"""
        logger.info(f"{self.agent_name} - Запуск...")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.bot.session.close()


# Пример использования
if __name__ == "__main__":
    import asyncio
    
    # Демонстрация структуры
    print("Telegram Agent модуль готов!")
    print("\nПример использования:")
    print("""
    from backend.bot.telegram_agent import TelegramAgent
    from backend.rag.rag_engine import RAGEngine
    
    # Инициализация RAG
    rag = RAGEngine(...)
    
    # Создание бота
    bot = TelegramAgent(
        bot_token='YOUR_TOKEN',
        rag_engine=rag,
        agent_name='Агент НТД'
    )
    
    # Запуск
    asyncio.run(bot.start())
    """)
