import telebot
import yt_dlp
import os

# Твій токен
TOKEN = '8566951931:AAEPXFvlgmfYkN1PduaAXXD9iRYRb90cpDA'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привіт! Я качаю відео з TikTok та YouTube.\n\n🚀 Просто кидай мені посилання!")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "http" not in url:
        bot.send_message(message.chat.id, "Це не схоже на посилання. Спробуй ще раз!")
        return

    msg = bot.send_message(message.chat.id, "⏳ Починаю завантаження, почекай трохи...")
    
    # Використовуємо папку /tmp для Render
    file_path = '/tmp/video.mp4'
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,
        'no_color': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Надсилаємо відео користувачу
        with open(file_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ Твоє відео готове!\n\n📢 Підпишись на мій канал, щоб підтримати проект!")
        
        # Видаляємо тимчасовий файл
        os.remove(file_path)
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)

bot.polling(none_stop=True)
