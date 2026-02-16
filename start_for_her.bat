@echo off
cd /d "C:\Users\vollk\Desktop\FdB\F_site\pro_j"
echo 🔥 ЗАПУСК ДЛЯ тебя!
echo ✅ ШАГ 1: Запускаю Django сервер...
start cmd /k "python manage.py runserver 0.0.0.0:8000"
timeout /t 3
echo ✅ ШАГ 2: Запускаю Ngrok для доступа из любой точки мира...
start cmd /k "ngrok http 8000"
echo ✅ ШАГ 3: Твой локальный IP:
ipconfig | findstr "IPv4"
echo.
echo 📱 Ссылка для локальной сети: http://localhost:8000
echo 🌍 Ngrok ссылка появится во втором окне!
echo.
pause