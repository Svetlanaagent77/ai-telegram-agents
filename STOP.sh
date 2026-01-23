#!/bin/bash
# ===================================================================
# AI Telegram Agents - Остановка (Linux/Mac)
# ===================================================================

echo ""
echo "===================================================================="
echo "     Остановка AI Telegram Agents"
echo "===================================================================="
echo ""

# Читаем PID
if [ -f .pids/bots.pid ]; then
    BOTS_PID=$(cat .pids/bots.pid)
    echo "Остановка ботов (PID: $BOTS_PID)..."
    kill $BOTS_PID 2>/dev/null
    rm .pids/bots.pid
    echo "✅ Боты остановлены"
else
    echo "⚠️  PID ботов не найден"
fi

if [ -f .pids/admin.pid ]; then
    ADMIN_PID=$(cat .pids/admin.pid)
    echo "Остановка админки (PID: $ADMIN_PID)..."
    kill $ADMIN_PID 2>/dev/null
    rm .pids/admin.pid
    echo "✅ Админка остановлена"
else
    echo "⚠️  PID админки не найден"
fi

echo ""
echo "===================================================================="
echo " ✅ Система остановлена"
echo "===================================================================="
echo ""
