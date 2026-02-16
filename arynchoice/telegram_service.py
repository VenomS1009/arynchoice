import requests
from django.conf import settings

def send_telegram_notification(user, activity, notes=""):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    message = f"🎉 НОВЫЙ ВЫБОР!\n\n"
    message += f"👤 Пользователь: {user.username}\n"
    message += f"🏷️ Активность: {activity.name}\n"
    message += f"💰 Стоимость: {activity.price} Аринкойнов\n"
    message += f"📅 Категория: {activity.category.name}\n"
    message += f"📍 Место: {activity.location}\n"
    message += f"⏰ Продолжительность: {activity.duration}\n"
    
    if notes:
        message += f"\n💭 Пожелания: {notes}\n"
    
    message += f"\n📊 Осталось Аринкойнов: {user.userprofile.arincoins}"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except:
        return False

def send_earn_notification(user, method, proof_text):
    """Отправка уведомления о новой заявке на заработок"""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    if not token or not chat_id:
        return False
    
    message = f"💰 НОВАЯ ЗАЯВКА НА ЗАРАБОТОК!\n\n"
    message += f"👤 Пользователь: {user.username}\n"
    message += f"🎯 Метод: {method.name}\n"
    message += f"🏆 Награда: {method.reward} Аринкойнов\n"
    message += f"📝 Описание: {method.description}\n\n"
    
    if proof_text:
        message += f"📎 Подтверждение:\n{proof_text}\n\n"
    
    # # Ссылка на админку для быстрой обработки
    # admin_url = f"https://dashboard.render.com/.../admin/arynchoice/earnrequest/"  
    # message += f"🔗 Обработать: {admin_url}"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        })
        return True
    except:
        return False