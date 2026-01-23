#!/usr/bin/env python3
"""
Проверка конфигурации - быстрая диагностика перед запуском
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import Config
from dotenv import load_dotenv

# Цвета для терминала
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def mask_key(key):
    """Маскировать API ключ для безопасного вывода"""
    if not key:
        return "НЕ НАЙДЕН"
    if len(key) < 10:
        return key
    return f"{key[:8]}...{key[-4:]}"

def check_env_file():
    """Проверка наличия .env файла"""
    print("\n" + "="*60)
    print("🔍 Проверка конфигурации")
    print("="*60)
    
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env файл не найден!")
        print_info("Создайте .env файл: cp .env.example .env")
        return False
    
    print_success(".env файл найден")
    return True

def check_api_keys():
    """Проверка API ключей"""
    print("\n📋 Проверка API ключей:")
    
    load_dotenv()
    
    issues = []
    
    # DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print_success(f"DeepSeek API: {mask_key(deepseek_key)}")
    else:
        print_error("DeepSeek API ключ не найден")
        issues.append("DEEPSEEK_API_KEY")
    
    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print_success(f"OpenAI API: {mask_key(openai_key)}")
    else:
        print_error("OpenAI API ключ не найден")
        issues.append("OPENAI_API_KEY")
    
    # Pinecone
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key:
        print_success(f"Pinecone API: {mask_key(pinecone_key)}")
    else:
        print_error("Pinecone API ключ не найден")
        issues.append("PINECONE_API_KEY")
    
    return issues

def check_telegram_tokens():
    """Проверка Telegram токенов"""
    print("\n🤖 Проверка Telegram ботов:")
    
    issues = []
    
    # Бот НТД
    token_ntd = os.getenv("TELEGRAM_BOT_TOKEN_NTD")
    if token_ntd and "СОЗДАЙ_БОТА" not in token_ntd:
        print_success(f"Бот НТД: {mask_key(token_ntd)}")
    else:
        print_error("Токен бота НТД не настроен")
        print_warning("Создайте бота через @BotFather и добавьте токен в .env")
        issues.append("TELEGRAM_BOT_TOKEN_NTD")
    
    # Бот Договоры
    token_docs = os.getenv("TELEGRAM_BOT_TOKEN_DOCS")
    if token_docs and "СОЗДАЙ_БОТА" not in token_docs:
        print_success(f"Бот Договоры: {mask_key(token_docs)}")
    else:
        print_error("Токен бота Договоры не настроен")
        print_warning("Создайте бота через @BotFather и добавьте токен в .env")
        issues.append("TELEGRAM_BOT_TOKEN_DOCS")
    
    return issues

def check_directories():
    """Проверка директорий для документов"""
    print("\n📁 Проверка директорий:")
    
    data_ntd = Path("data/ntd")
    data_docs = Path("data/docs")
    
    if data_ntd.exists():
        files = list(data_ntd.glob("*.pdf")) + list(data_ntd.glob("*.docx"))
        print_success(f"data/ntd/ найдена ({len(files)} документов)")
    else:
        print_warning("data/ntd/ не найдена")
        print_info("Создайте: mkdir -p data/ntd")
    
    if data_docs.exists():
        files = list(data_docs.glob("*.pdf")) + list(data_docs.glob("*.docx"))
        print_success(f"data/docs/ найдена ({len(files)} документов)")
    else:
        print_warning("data/docs/ не найдена")
        print_info("Создайте: mkdir -p data/docs")

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n📦 Проверка зависимостей:")
    
    required = [
        "openai",
        "pinecone",
        "aiogram",
        "python-dotenv"
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} установлен")
        except ImportError:
            print_error(f"{package} не установлен")
            missing.append(package)
    
    if missing:
        print_warning(f"\nУстановите: pip install {' '.join(missing)}")
    
    return missing

def main():
    """Главная функция"""
    
    # Проверка .env
    if not check_env_file():
        print("\n" + "="*60)
        print_error("Конфигурация не готова!")
        print_info("Следуйте инструкциям выше для настройки")
        print("="*60)
        sys.exit(1)
    
    # Проверка API ключей
    api_issues = check_api_keys()
    
    # Проверка Telegram
    telegram_issues = check_telegram_tokens()
    
    # Проверка директорий
    check_directories()
    
    # Проверка зависимостей
    missing_deps = check_dependencies()
    
    # Итоги
    print("\n" + "="*60)
    
    all_issues = api_issues + telegram_issues
    
    if all_issues or missing_deps:
        print_error("❌ Конфигурация не готова к запуску!")
        print("\n📝 Что нужно исправить:")
        
        if api_issues:
            print(f"\n   API ключи: {', '.join(api_issues)}")
            print("   Откройте .env и добавьте недостающие ключи")
        
        if telegram_issues:
            print(f"\n   Telegram боты: {', '.join(telegram_issues)}")
            print("   Инструкция: см. TELEGRAM_BOTS.md")
        
        if missing_deps:
            print(f"\n   Зависимости: {', '.join(missing_deps)}")
            print("   Установите: pip install -r requirements.txt")
        
        print("\n" + "="*60)
        sys.exit(1)
    
    else:
        print_success("🎉 Конфигурация полностью готова!")
        print("\n🚀 Следующие шаги:")
        print("   1. Загрузите документы:")
        print("      python backend/utils/upload_documents.py --agent ntd --directory data/ntd")
        print("   2. Запустите систему:")
        print("      python main.py")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()
