# bot.py

import telebot
import service
from instagram_links import get_links_from_message, get_tuple_of_sources_by_account, get_source_by_link
import logging

bot = telebot.TeleBot(token=service.telegram_token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, service.welcome_message)

@bot.message_handler(content_types=['text'])
def handle_message(message):
    account_links, image_links = get_links_from_message(message.text)
    sources = []
    for account_link in account_links:
        sources_by_account_link = get_tuple_of_sources_by_account(account_link)
        if sources_by_account_link:
            sources.extend(sources_by_account_link)
    for image_link in image_links:
        source = get_source_by_link(image_link)
        if source:
            sources.append(source)
    for i, link in enumerate(sources):
        bot.send_message(message.chat.id, '<a href="{}">{}</a>'.format(link, i), parse_mode='HTML')

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
bot.polling(non_stop=True)  # Исправлено на non_stop
