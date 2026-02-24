import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp

# Налаштування логування (щоб бачити помилки в Render Logs)
logging.basicConfig(level=logging.INFO)

# Твій токен від @BotFather
API_TOKEN = 'ТВІЙ_ТОКЕН_ТУТ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Налаштування "маскування" під браузер
YDL_OPTIONS = {
    'format': 'best',
    'outtmpl': 'video.mp4',
    'noplaylist': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'quiet': True
}

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Привіт! Я працюю 24/7. Пришліть мені посилання на відео (YouTube, TikTok, Insta), і я його завантажу.")

@dp.message_handler()
async def handle_video(message: types.Message):
    url = message.text
    if not url.startswith("http"):
        await message.answer("Будь ласка, надішліть коректне посилання.")
        return

    status_msg = await message.answer("⏳ Обробляю запит, зачекайте...")

    try:
        # Завантаження відео
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([url])
        
        # Відправка файлу
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as video:
                await message.answer_video(video, caption="Ось ваше відео! ✅")
            os.remove("video.mp4") # Видаляємо, щоб не забивати пам'ять сервера
        else:
            await message.answer("Помилка: файл не завантажився.")

    except Exception as e:
        await message.answer(f"Сталася помилка при завантаженні: {str(e)}")
    
    await status_msg.delete()

if __name__ == '__main__':
    print("Бот запущений...")
    executor.start_polling(dp, skip_updates=True)
    
