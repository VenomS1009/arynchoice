#!/bin/bash

echo "==================================="
echo "🚀 Запуск ArynChoice на Render.com"
echo "==================================="

echo "📦 Установка зависимостей..."
pip install -r requirements.txt

echo "🗄️  Применение миграций..."
python manage.py migrate --noinput

echo "🎨 Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "🤖 Отправка уведомления в Telegram..."

python manage.py shell <<EOF
import os
import requests
import socket
from time import sleep

sleep(2)

token = os.environ.get('8548512803:AAHO7DoppUOW2yh2igMnynmrNpuEPII1-Sw')
chat_id = os.environ.get('584906132')
hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')

if token and chat_id and hostname:
    url = f"https://{hostname}"
    
    message = f"""
💖 **ArynChoice запущен!** 💖

🌍 **Render.com**
🔗 **Постоянная ссылка:**
{url}

📱 Открывай в любое время!

✨ Выбирай наши приключения!

"""
    
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={{
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Уведомление отправлено в Telegram!")
            print(f"🔗 Ссылка: {url}")
        else:
            print(f"❌ Ошибка Telegram: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
else:
    print("⚠️ Telegram не настроен")
EOF

echo "==================================="
echo "✅ Запуск Gunicorn..."
echo "==================================="

exec gunicorn pro_j.wsgi:application --bind 0.0.0.0:$PORT