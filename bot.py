from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import os
import instaloader

TOKEN = os.getenv('TELEGRAM_TOKEN')
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Отправь мне ссылку на рилс из Instagram.')

def download_reels(update: Update, context: CallbackContext):
    url = update.message.text
    if 'instagram.com/reel/' in url:
        try:
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])
            L.download_post(post, target=f"./{post.shortcode}")
            video_path = f"./{post.shortcode}/{post.shortcode}.mp4"

            if os.path.exists(video_path):
                update.message.reply_video(video=open(video_path, 'rb'))
                os.remove(video_path)
                os.rmdir(f"./{post.shortcode}")
            else:
                update.message.reply_text('Не удалось найти видео.')
        except Exception as e:
            update.message.reply_text(f'Произошла ошибка: {e}')
    else:
        update.message.reply_text('Пожалуйста, отправьте корректную ссылку на рилс из Instagram.')

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reels))

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
