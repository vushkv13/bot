from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import os
import pyinstagram as pyi

# Получение токена и данных для входа из переменных окружения
TOKEN = os.getenv('TELEGRAM_TOKEN')
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Инициализация бота Telegram
bot = Bot(token=TOKEN)

# Функция для получения видео по идентификатору медиа
def get_video(media_id: str):
    client = pyi.InstagramClient(username=USERNAME, password=PASSWORD)
    client.login()

    # Пример получения медиа по идентификатору
    media = client.get_media(media_id)
    if media.is_video:
        return media.video_url
    return None

# Обработчик команд Telegram
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Отправь мне ссылку на reel из Instagram, и я верну видео.")

# Обработчик сообщений Telegram
def echo(update: Update, context: CallbackContext):
    match = re.search(r'/reel/([^/?]+)', update.message.text)
    if match:
        media_id = match.group(1)
        video_url = get_video(media_id)
        if video_url:
            bot.send_message(chat_id=update.effective_chat.id, text=f'Смотрите видео здесь: {video_url}')
        else:
            bot.send_message(chat_id=update.effective_chat.id, text='Не удалось получить видео. Попробуйте снова.')
    else:
        bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, отправьте корректную ссылку на reel из Instagram.')

# Создание обработчика команды /start
start_handler = CommandHandler('start', start)

# Создание обработчика сообщений
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

# Инициализация Telegram-бота
updater = Updater(TOKEN, use_context=True)

# Добавление обработчиков команд и сообщений в Telegram-бота
dispatcher = updater.dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)

# Запуск бота Telegram
updater.start_polling()
updater.idle()
