import telebot
import Token
import random
from telebot import types
import logging

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(Token.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Рандомное число")
        item2 = types.KeyboardButton("Как дела?")
        markup.add(item1, item2)

        bot.send_message(message.chat.id,
                         "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, ваш личный бот.".format(
                             message.from_user, bot.get_me()),
                         parse_mode='html', reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка в welcome: {e}")

@bot.message_handler(content_types='text')
def lalala(message):
    try:
        if message.chat.type == 'private':
            if message.text == 'Рандомное число':
                bot.send_message(message.chat.id, str(random.randint(0, 100)))
            elif message.text == "Как дела?":
                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
                item2 = types.InlineKeyboardButton("Не очень", callback_data='bad')
                markup.add(item1, item2)
                bot.send_message(message.chat.id, 'Отлично, сам как?', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f'Вы сказали: {message.text}')
    except Exception as e:
        logging.error(f"Ошибка в lalala: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Вот и прекрасно')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Бывает, держись, дружище!')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message_id, text="Как дела?",
                                  reply_markup=None)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="СИИИИИИИИ")
    except Exception as e:
        logging.error(f"Ошибка в callback_inline: {e}")

if __name__ == '__main__':
    bot.polling(none_stop=True)