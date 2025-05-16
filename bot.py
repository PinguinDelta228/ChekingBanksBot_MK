import telebot
import Token
from telebot import types
import logging

import telebot
import requests
import redis
import Token
from telebot import types
import logging

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(Token.TOKEN)
cache = redis.Redis(host='localhost', port=6379, db=0)
def get_bank_info(bank_identifier):
    cached_data = cache.get(bank_identifier)
    if cached_data:
        return cached_data.decode('utf-8')
    
    url = f"https://api.example.com/banks/{bank_identifier}"  
    response = requests.get(url)

    if response.status_code == 200:
        bank_info = response.json()
        cache.setex(bank_identifier, 3600, str(bank_info))
    else:
        return None

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Запросить информацию о банке")
        markup.add(item1)

        bot.send_message(message.chat.id,
                         "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, ваш личный бот.".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка в welcome: {e}")

@bot.message_handler(content_types='text')
def handle_text(message):
    try:
        if message.chat.type == 'private':
            if message.text == "Запросить информацию о банке":
                bot.send_message(message.chat.id, "Введите название банка или его идентификатор:")
            else:
                bank_info = get_bank_info(message.text.strip())
                if bank_info:
                    response_message = (
                        f"Информация о банке:\n"
                        f"Название: {bank_info['name']}\n"
                        f"Корреспондентский счет: {bank_info['correspondent_account']}\n"
                        f"Адрес: {bank_info['address']}\n"
                        f"Статус: {bank_info['status']}"
                    )
                    bot.send_message(message.chat.id, response_message)
                else:
                    bot.send_message(message.chat.id, "Банк не найден или произошла ошибка при запросе.")
    except Exception as e:
        logging.error(f"Ошибка в handle_text: {e}")

if __name__ == '__main__':
    bot.polling(none_stop=True)