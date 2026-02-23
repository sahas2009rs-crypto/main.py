import telebot
import yt_dlp
import os
import http.server
import socketserver
import threading

# --- 1. ЗАПОБІЖНИК ДЛЯ RENDER (щоб не вибивало помилку Port Scan) ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# --- 2. НАЛАШТУВАННЯ БОТА ---
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
CHANNEL_ID = '@Pyhnastipets' # Твій новий канал
bot = telebot.TeleBot(TOKEN)

# Функція перевірки підписки
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        # Якщо бот ще не адмін, він дозволить користуватися (тимчасово)
        return True 

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"👋 **Привіт! Я допоможу тобі скачати відео.**\n\n"
        f"✅ **Для використання бота підпишись на наш канал:**\n"
        f"👉 https://t.me/Pyhnastipets\n\n"
        f"Після підписки просто скидай посилання (через 'Поділитися' в TikTok) і я відправлю тобі файл! 🚀"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # Перевірка на підписку
    if not check_sub(user_id):
        bot.send_message(message.chat.id, f"❌ **Доступ обмежено!**\n\nБудь ласка, спочатку підпишись на канал: https://t.me/Pyhnastipets")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Надішли мені посилання на відео через кнопку 'Поділитися'!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Починаю завантаження відео, почекай...")
    file_path = '/tmp/video.mp4'
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"✅ Готово! Підписуйся на @Pyhnastipets")
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception:
        bot.send_message(message.chat.id, "❌ Помилка завантаження. Спробуй ще раз пізніше.")

bot.polling(none_stop=True)
