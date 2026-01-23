"""
Telegram Bot для AI-агентов
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from typing import Optional
import sys
import os

# Добавляем путь к backend
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.rag_engine import RAGEngine


class TelegramAIBot:
    """
    Telegram бот с RAG-поиском
    """
    
    def __init__(self, token: str, agent_name: str, rag_engine: RAGEngine):
        """
        Args:
            token: Telegram bot token
            agent_name: Название агента (НТД или Договоры)
            rag_engine: RAG движок для поиска
        """
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.agent_name = agent_name
        self.rag = rag_engine
        
        # Регистрируем обработчики
        self._register_handlers()
        
        logging.info(f"✓ Telegram бот '{agent_name}' инициализирован")
    
    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            """Команда /start"""
            await message.answer(
                f"👋 Привет! Я AI-ассистент по базе знаний *{self.agent_name}*.\n\n"
                f"Задай мне вопрос, и я найду ответ в документах.\n\n"
                f"Доступные команды:\n"
                f"/start - начало работы\n"
                f"/help - помощь\n"
                f"/stats - статистика",
                parse_mode="Markdown"
            )
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            """Команда /help"""
            help_text = (
                f"*Как пользоваться ботом {self.agent_name}:*\n\n"
                f"1️⃣ Просто напиши свой вопрос\n"
                f"2️⃣ Бот найдет релевантную информацию\n"
                f"3️⃣ Получишь ответ с указанием источников\n\n"
                f"*Примеры вопросов:*\n"
            )
            
            if self.agent_name == "НТД":
                help_text += (
                    f"• Какие требования ГОСТ 12345 к материалу X?\n"
                    f"• Найди информацию по СНиП о нагрузках\n"
                    f"• Что говорит регламент о сроках испытаний?"
                )
            else:
                help_text += (
                    f"• Какие условия оплаты в договоре с компанией X?\n"
                    f"• Найди информацию о сроках поставки\n"
                    f"• Какая ответственность за нарушение сроков?"
                )
            
            await message.answer(help_text, parse_mode="Markdown")
        
        @self.dp.message(Command("stats"))
        async def cmd_stats(message: Message):
            """Команда /stats"""
            # TODO: добавить реальную статистику из БД
            await message.answer(
                f"📊 *Статистика бота {self.agent_name}:*\n\n"
                f"Документов в базе: ~XX\n"
                f"Вопросов обработано: ~XX\n"
                f"Средняя точность: ~XX%",
                parse_mode="Markdown"
            )
        
        @self.dp.message(F.text)
        async def handle_question(message: Message):
            """Обработка вопросов пользователя"""
            
            # Показываем, что бот печатает
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            question = message.text
            
            try:
                # Поиск и генерация ответа через RAG
                result = self.rag.process_query(question, top_k=3)
                
                answer = result['answer']
                sources = result['sources']
                confidence = result['confidence']
                
                # Формируем ответ
                response = f"*Ответ:*\n\n{answer}\n\n"
                
                # Добавляем источники
                if sources:
                    response += "*Источники:*\n"
                    for i, source in enumerate(sources[:3], 1):
                        doc_type = source['metadata'].get('doc_type', 'Документ')
                        doc_number = source['metadata'].get('doc_number', '')
                        score = source['score']
                        
                        response += f"{i}. {doc_type}"
                        if doc_number:
                            response += f" №{doc_number}"
                        response += f" (релевантность: {score:.2f})\n"
                
                # Отправляем ответ
                await message.answer(response, parse_mode="Markdown")
                
                # Кнопки обратной связи
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="👍 Полезно", callback_data="feedback_good"),
                        types.InlineKeyboardButton(text="👎 Не то", callback_data="feedback_bad")
                    ]
                ])
                
                await message.answer(
                    "Был ли ответ полезен?",
                    reply_markup=keyboard
                )
            
            except Exception as e:
                logging.error(f"Ошибка обработки вопроса: {e}")
                await message.answer(
                    "😔 Произошла ошибка при обработке вопроса. Попробуйте еще раз.",
                    parse_mode="Markdown"
                )
        
        @self.dp.callback_query(F.data.startswith("feedback_"))
        async def handle_feedback(callback: types.CallbackQuery):
            """Обработка обратной связи"""
            feedback_type = callback.data.split("_")[1]
            
            if feedback_type == "good":
                await callback.answer("Спасибо за отзыв! 👍")
            else:
                await callback.answer("Спасибо! Мы улучшим ответы. 👎")
            
            # TODO: Сохранить отзыв в БД
            await callback.message.edit_reply_markup(reply_markup=None)
    
    async def start(self):
        """Запуск бота"""
        logging.info(f"🚀 Запуск бота '{self.agent_name}'...")
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Остановка бота"""
        logging.info(f"🛑 Остановка бота '{self.agent_name}'...")
        await self.bot.session.close()


async def main():
    """
    Запуск обоих ботов одновременно
    """
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # TODO: Загрузить из .env
    TOKEN_NTD = os.getenv("TELEGRAM_BOT_TOKEN_NTD")
    TOKEN_DOCS = os.getenv("TELEGRAM_BOT_TOKEN_DOCS")
    
    if not TOKEN_NTD or not TOKEN_DOCS:
        print("❌ Ошибка: не заданы токены ботов в .env")
        print("Установите TELEGRAM_BOT_TOKEN_NTD и TELEGRAM_BOT_TOKEN_DOCS")
        return
    
    # Создаем RAG engines (пока без реальной инициализации)
    rag_ntd = RAGEngine(ai_provider="openai", model="gpt-4")
    rag_docs = RAGEngine(ai_provider="openai", model="gpt-4")
    
    # Создаем ботов
    bot_ntd = TelegramAIBot(TOKEN_NTD, "НТД", rag_ntd)
    bot_docs = TelegramAIBot(TOKEN_DOCS, "Договоры", rag_docs)
    
    # Запускаем оба бота одновременно
    await asyncio.gather(
        bot_ntd.start(),
        bot_docs.start()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Боты остановлены")
