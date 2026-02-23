import telebot
import yt_dlp
import os

# --- НАЛАШТУВАННЯ ---
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
CHANNEL_ID = '@animals5323' # Твій канал про тварин
bot = telebot.TeleBot(TOKEN)

# Функція перевірки підписки
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        # Якщо бот не адмін, він не зможе перевірити підписку
        return True 

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"👋 **Вітаю!**\n\n"
        f"❗ **Для продовження підпишись на мій канал:** {CHANNEL_ID}\n\n"
        f"Після підписки просто надішли мені посилання на відео через кнопку 'Поділитися' в TikTok! 🚀"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # Перевірка на підписку
    if not check_sub(user_id):
        bot.send_message(message.chat.id, f"❌ **Ви не підписані!**\n\nБудь ласка, підпишіться на канал {CHANNEL_ID}, щоб скачати відео.")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Надішли посилання через 'Поділитися' в TikTok!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Починаю завантаження відео...")
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
            # Тільки відео та назва каналу
            bot.send_video(message.chat.id, video, caption=f"✅ Готово! {CHANNEL_ID}")
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception:
        bot.send_message(message.chat.id, "❌ Помилка завантаження. Спробуй ще раз через 'Поділитися'.")

bot.polling(none_stop=True)
    
