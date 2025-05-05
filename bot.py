import telebot
import requests
import redis
import Token
from telebot import types
import logging
from dadata import Dadata
from bank_info_handler import save_bank_info_to_json  # Импортируем функцию сохранения

# Настройка логирования
logging.basicConfig(level=logging.INFO)

dadata_token = "965d5511523853d8eeab7a0c3f0d455ca37ed4e7" #токен Dadata
dadata = Dadata(dadata_token)
bot = telebot.TeleBot(Token.TOKEN) # Использует токен из Token.py
# cache = redis.Redis(host='localhost', port=6379, db=0) # Раскомментируйте, если используете Redis

def get_bank_info(bank_identifier):
    try:
        # Сначала пробуем найти по БИК
        result = dadata.bank(bank_identifier)
        if result and result[0]['data']:
             return result[0]['data']

        # Если не найдено по БИК, пробуем найти по названию или другому идентификатору
        result = dadata.find_by_id("bank", bank_identifier)
        if result and 'suggestions' in result and result['suggestions']:
            return result['suggestions'][0]['data']
        else:
            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к Dadata: {e}")
        return None

def format_bank_info(bank_info):
    name = bank_info.get('name', {}).get('short', 'Неизвестно')
    bic = bank_info.get('bic', 'Неизвестно')
    swift = bank_info.get('swift', 'Неизвестно')
    inn = bank_info.get('inn', 'Неизвестно')
    kpp = bank_info.get('kpp', 'Неизвестно')
    correspondent_account = bank_info.get('correspondent_account', 'Неизвестно')
    address = bank_info.get('address', {}).get('value', 'Неизвестно')

    return (f"Название: {name}\n"
            f"BIC: {bic}\n"
            f"SWIFT: {swift}\n"
            f"ИНН: {inn}\n"
            f"КПП: {kpp}\n"
            f"Корреспондентский счет: {correspondent_account}\n"
            f"Адрес: {address}")

def send_safe_message(chat_id, text, reply_markup=None):
    try:
        bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        if "403" in str(e):
            logging.warning(f"Не удалось отправить сообщение чату {chat_id}: пользователь заблокировал бота.")
        else:
            logging.error(f"Ошибка при отправке сообщения: {e}")

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Запросить информацию о банке")
        item2 = types.KeyboardButton("Найти все банки")
        markup.add(item1, item2)

        send_safe_message(message.chat.id,
                         f"Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>{bot.get_me().first_name}</b>, ваш личный бот.",
                         reply_markup=markup)
    except Exception as e:
        logging.error(f"Ошибка в welcome: {e}")

@bot.message_handler(content_types='text')
def handle_text(message):
    try:
        if message.chat.type == 'private':
            if message.text == "Запросить информацию о банке":
                send_safe_message(message.chat.id, "Введите БИК или название банка:")
            elif message.text == "Найти все банки":
                banks = get_all_banks()
                if banks is not None and len(banks) > 0:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    #'value' для отображения названия банка
                    for bank in banks:
                        if 'value' in bank:
                            bank_button = types.KeyboardButton(bank['value'])
                            markup.add(bank_button)
                    send_safe_message(message.chat.id, "Выберите банк из списка:", reply_markup=markup)
                else:
                    send_safe_message(message.chat.id, "Не удалось получить список банков.")
            else:
                # Обрабатываем введенный текст как запрос на информацию о банке
                bank_info = get_bank_info(message.text.strip())
                if bank_info:
                    response_message = f"Информация о банке:\n{format_bank_info(bank_info)}"
                    send_safe_message(message.chat.id, response_message)
                    # Сохраняем информацию о банке в JSON
                    save_bank_info_to_json(bank_info)
                else:
                    send_safe_message(message.chat.id, "Банк не найден или произошла ошибка при запросе.")
    except Exception as e:
        logging.error(f"Ошибка в handle_text: {e}")
        send_safe_message(message.chat.id, "Произошла ошибка при обработке вашего запроса.")


def get_all_banks():
    try:
        # Запрос к API Dadata для получения списка банков (может вернуть только небольшое количество)
        url = "http://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/bank"
        # Пустой запрос или небольшой query может вернуть некоторые банки, но полного списка через этот метод получить сложно.
        response = requests.post(url, headers={"Authorization": f"Token {dadata_token}"}, json={"query": ""})

        logging.info(f"Запрос к {url} завершился с кодом {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            # Dadata возвращает список предложений в поле 'suggestions'
            banks = data.get("suggestions", [])
            logging.info(f"Получено предложений банков: {len(banks)}")
            return banks
        else:
            logging.error(f"Ошибка при запросе к API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Ошибка в get_all_banks: {e}")
        return None

if __name__ == '__main__':
    bot.polling(none_stop=True)