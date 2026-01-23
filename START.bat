@echo off
REM ===================================================================
REM AI Telegram Agents - Автозапуск (Windows)
REM ===================================================================

echo.
echo ====================================================================
echo      AI TELEGRAM AGENTS - Запуск системы
echo ====================================================================
echo.

REM Проверка Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Проверка зависимостей...
python -c "import fastapi, aiogram, openai, pinecone" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Установка зависимостей...
    pip install -r requirements.txt
)

echo [2/3] Запуск Telegram ботов...
start "AI Agents - Bots" python main.py

timeout /t 3 /nobreak >nul

echo [3/3] Запуск веб-админки...
start "AI Agents - Admin Panel" python admin_panel.py

timeout /t 3 /nobreak >nul

echo.
echo ====================================================================
echo  СИСТЕМА ЗАПУЩЕНА!
echo ====================================================================
echo.
echo  Telegram боты работают
echo  Веб-админка: http://localhost:8000
echo.
echo  Для остановки закройте оба окна
echo ====================================================================
echo.

pause
