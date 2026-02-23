import telebot
import yt_dlp
import os
import http.server
import socketserver
import threading
import time

# --- 1. ОЖИВЛЮВАЧ ДЛЯ RENDER (Щоб не засинав) ---
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
    try: bot.send_message(MY_ID, f"🔔 Юзер {message.from_user.first_name} зайшов у бот")
    except: pass
    text = (f"👋 **Вітаю! Я скачаю відео без водяного знаку.**\n\n"
            f"✅ **Підпишись на канал:** https://t.me/Pyhnastipets\n"
            f"🚀 **Потім просто надішли посилання!**")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Підпишись на https://t.me/Pyhnastipets")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Це не посилання!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Обходжу захист та завантажую відео...")
    file_path = f"video_{message.from_user.id}.mp4"

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✅ Готово для @Pyhnastipets")
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Помилка завантаження.", message.chat.id, msg.message_id)
    except:
        bot.send_message(message.chat.id, "❌ Не вдалося скачати. Можливо, відео приватне.")

# --- 3. ТОЙ САМИЙ "ВІЧНИЙ ЦИКЛ" (ЗУБ ДАЮ, ПРАЦЮВАТИМЕ) ---
while True:
    try:
        print("Бот запущений...")
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Помилка: {e}. Перезапуск через 5 секунд...")
        time.sleep(5)
        
