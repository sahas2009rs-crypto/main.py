import telebot
import yt_dlp
import os
import http.server
import socketserver
import threading

# --- 1. ОЖИВЛЮВАЧ ДЛЯ RENDER ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving on port {port}")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# --- 2. НАЛАШТУВАННЯ БОТА ---
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
CHANNEL_ID = '@Pyhnastipets' # Твій канал
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return True 

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"👋 **Привіт!**\n\n"
        f"❗ **Для продовження підпишись на мій канал:**\n"
        f"👉 https://t.me/Pyhnastipets\n\n"
        f"Після підписки просто надішли мені посилання на відео з TikTok! 🚀"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if not check_sub(user_id):
        bot.send_message(message.chat.id, f"❌ **Ви не підписані!**\n\nБудь ласка, підпишіться на канал: https://t.me/Pyhnastipets")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Надішли посилання!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Завантажую...")
    file_path = '/tmp/video.mp4'
    
    ydl_opts = {'format': 'best', 'outtmpl': file_path}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption=f"✅ Готово!")
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception:
        bot.send_message(message.chat.id, "❌ Помилка завантаження.")

bot.polling(none_stop=True)
                         
