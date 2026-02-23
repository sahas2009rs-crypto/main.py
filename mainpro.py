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
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# --- 2. НАЛАШТУВАННЯ ---
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
CHANNEL_ID = '@Pyhnastipets' 
MY_ID = 5124018742 
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return True 

@bot.message_handler(commands=['start'])
def start(message):
    try: bot.send_message(MY_ID, f"🔔 Новий юзер: {message.from_user.first_name}")
    except: pass
    text = (f"👋 **Привіт!**\n\n❗ **Для роботи підпишись:** https://t.me/Pyhnastipets\n\n"
            f"Потім просто скинь посилання на відео! 🚀")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Спочатку підпишись на https://t.me/Pyhnastipets")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Це не посилання!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Завантажую...")
    file_path = 'video.mp4'

    # --- НАЛАШТУВАННЯ ДЛЯ ОБХОДУ БЛОКУВАНЬ ---
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.tiktok.com/',
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ Готово!")
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Спробуй інше відео.")
        print(f"Помилка: {e}")

bot.polling(none_stop=True)
    
