import telebot
import yt_dlp
import os

# --- ТВОЇ НАЛАШТУВАННЯ ---
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
CHANNEL_ID = '@ТВІЙ_КАНАЛ' # Сашо, обов'язково впиши сюди назву свого каналу з @
bot = telebot.TeleBot(TOKEN)

# 1. Функція перевірки підписки
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        # Якщо бот не адмін або сталася помилка, дозволяємо скачувати
        return True 

# 2. Команда /start з твоєю інструкцією
@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"👋 **Привіт! Я допоможу тобі швидко скачати відео.**\n\n"
        f"📢 **Умова роботи:** підпишись на наш канал: {CHANNEL_ID}\n\n"
        f"📖 **ЯК ПРАВИЛЬНО СКАЧАТИ ВІДЕО (Твій спосіб):**\n"
        f"1️⃣ Відкрий TikTok на потрібному відео.\n"
        f"2️⃣ Натисни кнопку **'Поділитися'** (Share).\n"
        f"3️⃣ У списку програм вибери **Telegram**.\n"
        f"4️⃣ Вибери цього бота і натисни **'Надіслати'**.\n\n"
        f"✅ Бот сам отримає посилання і відправить тобі відео файл!"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# 3. Обробка посилань та завантаження
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
    # Перевірка на підписку
    if not check_sub(user_id):
        bot.send_message(message.chat.id, f"⚠️ **Доступ обмежено!**\n\nСпочатку підпишись на наш канал {CHANNEL_ID}, щоб бот запрацював.")
        return

    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "🧐 Це не посилання. Спробуй через кнопку 'Поділитися' в TikTok!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Починаю магію завантаження, зачекай пару секунд...")
    file_path = '/tmp/video.mp4'
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'no_color': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Надсилаємо відео з автоматичною рекламою твого каналу
        with open(file_path, 'rb') as video:
            bot.send_video(
                message.chat.id, 
                video, 
                caption=f"✅ Відео завантажено успішно!\n\n🚀 Більше крутого контенту тут: {CHANNEL_ID}"
            )
        
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception:
        bot.send_message(message.chat.id, "❌ Помилка завантаження. Спробуй ще раз через 'Поділитися'.")

bot.polling(none_stop=True)
    
