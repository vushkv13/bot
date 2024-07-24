import instaloader
import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Информация о канале
CHANNEL_ID = os.getenv('CHANNEL_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Функция проверки подписки
async def check_subscription(update: Update, context: CallbackContext) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        return False

# Команда start
async def start(update: Update, context: CallbackContext):
    if await check_subscription(update, context):
        await update.message.reply_text('Привет! Отправь мне ссылку на видео из Instagram.')
    else:
        keyboard = [[InlineKeyboardButton("Подписаться", url=f'https://t.me/{CHANNEL_ID.lstrip("@")}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Для использования бота, подпишитесь на канал.', reply_markup=reply_markup)

# Функция для извлечения короткого кода из ссылки
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(reel|p)/([^/]+)/", url)
    return match.group(2) if match else None

# Обработчик сообщений с ссылками
async def handle_message(update: Update, context: CallbackContext):
    if await check_subscription(update, context):
        url = update.message.text
        shortcode = extract_shortcode(url)
        if shortcode:
            try:
                loader = instaloader.Instaloader()

                # Вход в аккаунт
                username = os.getenv('INSTAGRAM_USERNAME')
                password = os.getenv('INSTAGRAM_PASSWORD')
                if username and password:
                    loader.login(username, password)

                post = instaloader.Post.from_shortcode(loader.context, shortcode)
                video_url = post.video_url
                if video_url:
                    await context.bot.send_video(chat_id=update.message.chat_id, video=video_url)
                else:
                    await update.message.reply_text('Это не видео. Пожалуйста, отправьте ссылку на видео.')
            except instaloader.exceptions.InstaloaderException as e:
                await update.message.reply_text('Не удалось скачать видео. Возможно, произошла ошибка с Instagram API.')
                logger.error(f"InstaloaderException: {e}")
            except Exception as e:
                await update.message.reply_text('Не удалось скачать видео. Убедитесь, что ссылка корректна.')
                logger.error(f"Error downloading video: {e}")
        else:
            await update.message.reply_text('Пожалуйста, отправьте корректную ссылку на пост в Instagram.')
    else:
        keyboard = [[InlineKeyboardButton("Подписаться", url=f'https://t.me/{CHANNEL_ID.lstrip("@")}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Для использования бота, подпишитесь на канал.', reply_markup=reply_markup)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
