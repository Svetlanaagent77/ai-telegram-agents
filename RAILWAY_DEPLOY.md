# 🚀 Деплой на Railway

## Быстрый старт (5 минут)

### 1. Создай проект на Railway

1. Зайди на https://railway.app
2. Войди через GitHub
3. New Project → Deploy from GitHub repo
4. Выбери репозиторий `ai-telegram-agents`

### 2. Добавь переменные окружения

В Railway Dashboard → Variables, добавь:

```
TELEGRAM_BOT_TOKEN_NTD=ваш-токен-бота-ntd
TELEGRAM_BOT_TOKEN_DOCS=ваш-токен-бота-docs

AI_PROVIDER=deepseek
AI_MODEL=deepseek-chat
DEEPSEEK_API_KEY=ваш-ключ-deepseek
DEEPSEEK_BASE_URL=https://api.deepseek.com

EMBEDDING_PROVIDER=voyage
VOYAGE_API_KEY=ваш-ключ-voyage
EMBEDDING_MODEL=voyage-multilingual-2
EMBEDDING_DIMENSION=1024

PINECONE_API_KEY=ваш-ключ-pinecone
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX=ai-agents-voyage

DEBUG=False
LOG_LEVEL=INFO
```

### 3. Создай индекс в Pinecone

⚠️ **ВАЖНО:** Voyage использует dimension=1024, а не 1536!

1. Зайди на https://app.pinecone.io
2. Create Index:
   - Name: `ai-agents-voyage`
   - Dimensions: `1024`
   - Metric: `cosine`
   - Serverless: `AWS us-east-1`

### 4. Деплой

Railway автоматически задеплоит при пуше в GitHub.

Проверь логи:
```
✅ Конфигурация проверена
✅ Voyage AI инициализирован: voyage-multilingual-2
✅ RAG для НТД готов (embeddings: voyage)
✅ RAG для Договоров готов (embeddings: voyage)
✅ Бот НТД создан
✅ Бот Договоры создан
🚀 Запуск ботов...
```

---

## Стоимость

### Railway
- $5/месяц (Hobby plan)
- Или бесплатно до $5 usage

### API
- **Voyage AI:** ~$0.06/1M токенов (эмбеддинги)
- **DeepSeek:** ~$0.14/1M токенов (генерация)
- **Pinecone:** FREE tier

**Итого при 100 запросов/день: ~$1-2/месяц**

---

## Troubleshooting

### "Module not found"
Railway должен автоматически установить зависимости из `requirements.txt`

### "Invalid API key"
Проверь переменные в Railway Dashboard → Variables

### Боты не отвечают
1. Проверь логи в Railway
2. Убедись что индекс Pinecone создан с dimension=1024
3. Загрузи документы через upload скрипт
