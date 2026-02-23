import telebot
import yt_dlp
import os
import http.server
import socketserver
import threading

# --- 1. ЖИТТЄЗАБЕЗПЕЧЕННЯ НА RENDER ---
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
    try: bot.send_message(MY_ID, f"🔔 Юзер {message.from_user.first_name} активував бота")
    except: pass
    text = (f"👋 **Привіт! Я скачаю для тебе відео з TikTok, Instagram та YouTube.**\n\n"
            f"✅ **Підпишись:** https://t.me/Pyhnastipets\n"
            f"🚀 **Потім просто скинь посилання!**")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"❌ Спочатку підпишись на наш канал: https://t.me/Pyhnastipets")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Надішли мені посилання!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Обходжу захист та завантажую відео... зазвичай це займає 10-20 секунд.")
    
    # Тимчасовий файл з унікальним ім'ям
    file_path = f"video_{message.from_user.id}.mp4"

    # --- СУПЕР-НАЛАШТУВАННЯ ДЛЯ ОБХОДУ ЗАХИСТУ ---
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise Exception("Не вдалося отримати дані")

        if os.path.exists(file_path):
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✅ Готово для @Pyhnastipets")
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ Не вдалося обробити це посилання. Спробуй інше відео.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Помилка сервісу. Можливо, відео приватне або занадто велике.", message.chat.id, msg.message_id)
        print(f"Error: {e}")

bot.polling(none_stop=True)
