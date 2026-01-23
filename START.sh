#!/bin/bash
# ===================================================================
# AI Telegram Agents - Автозапуск (Linux/Mac)
# ===================================================================

echo ""
echo "===================================================================="
echo "     AI TELEGRAM AGENTS - Запуск системы"
echo "===================================================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ОШИБКА: Python 3 не найден!"
    echo "Установите Python: https://www.python.org/downloads/"
    exit 1
fi

# Проверка зависимостей
echo "[1/3] Проверка зависимостей..."
python3 -c "import fastapi, aiogram, openai, pinecone" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Установка зависимостей..."
    pip3 install -r requirements.txt
fi

# Запуск ботов в фоне
echo "[2/3] Запуск Telegram ботов..."
nohup python3 main.py > logs/bots.log 2>&1 &
BOTS_PID=$!
echo "✅ Боты запущены (PID: $BOTS_PID)"

sleep 2

# Запуск админки в фоне
echo "[3/3] Запуск веб-админки..."
nohup python3 admin_panel.py > logs/admin.log 2>&1 &
ADMIN_PID=$!
echo "✅ Админка запущена (PID: $ADMIN_PID)"

sleep 2

echo ""
echo "===================================================================="
echo " ✅ СИСТЕМА ЗАПУЩЕНА!"
echo "===================================================================="
echo ""
echo "  📱 Telegram боты работают"
echo "  🌐 Веб-админка: http://localhost:8000"
echo ""
echo "  📊 Логи:"
echo "     Боты:    tail -f logs/bots.log"
echo "     Админка: tail -f logs/admin.log"
echo ""
echo "  🛑 Остановка:"
echo "     ./STOP.sh"
echo ""
echo "===================================================================="
echo ""

# Сохраняем PID для остановки
echo "$BOTS_PID" > .pids/bots.pid
echo "$ADMIN_PID" > .pids/admin.pid
