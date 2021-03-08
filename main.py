import telebot
import database
import validation
if __name__ == "__main__":
    bot = telebot.TeleBot('1608185959:AAEOTN992X9fP1WFPxyvFmZKMQmIc37rmHU')


    @bot.message_handler(commands=['start'])
    def reply_to_message(message):
        """Запуск чата с ботом"""
        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('Найти билет', 'Список городов')
        bot.send_message(
            message.chat.id,
            f'Здравствуйте, {message.from_user.first_name}! Я бот, который найдет "САМЫЙ" дешевый авиабилет для тебя.',
            reply_markup=keyboard)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        """Отправляет сообщение"""
        user_id = message.from_user.id
        if not database.Database().user_exist(user_id):
            database.Database().add_user(user_id)
        
        if message.text.lower() == "список городов":
            cities = database.Database().get_city_list()
            cities = "\n".join(cities)
            bot.send_message(user_id, f'Список поддерживаемых городов:\n{cities}')
        
        elif message.text.lower() == "найти билет":
            database.Database().set_last_to_for_user(user_id, "Null")
            database.Database().set_last_from_for_user(user_id, "Null")
            database.Database().set_last_date_for_user(user_id, "Null")
            keyboard = telebot.types.ReplyKeyboardMarkup(True)
            for city in database.Database().get_city_list():
                keyboard.row(city)
            bot.send_message(user_id, 'Из какого города вы хотите вылететь?',reply_markup=keyboard)
            
        elif database.Database().get_last_from_for_user(user_id) is None:
            if database.Database().city_exist(city_name=message.text.lower()):
                city_id = database.Database().city_id_by_city_name(city_name=message.text.lower())
                database.Database().set_last_from_for_user(user_id, city_id)
                keyboard = telebot.types.ReplyKeyboardMarkup(True)
                for city in database.Database().get_city_list():
                    keyboard.row(city)
                bot.send_message(user_id, 'В какой город вы хотите прилететь?',reply_markup=keyboard)
            else:
                bot.send_message(user_id, "К сожалению я не могу найти этот город в своей базе.:(")
                bot.send_message(user_id, 'Можете ввести другой город или снова этот если вы ошиблись.')
        
        elif database.Database().get_last_to_for_user(user_id) is None:
            if database.Database().city_exist(city_name=message.text.lower()):
                city_id = database.Database().city_id_by_city_name(city_name=message.text.lower())
                database.Database().set_last_to_for_user(user_id, city_id)
                bot.send_message(user_id, 'В какой день вы хотите полететь? (Например 14.01.2021)')
            else:
                bot.send_message(user_id, "К сожалению я не могу найти этот город в своей базе.:(")
                bot.send_message(user_id, 'Можете ввести другой город или снова этот если вы ошиблись.')

        elif database.Database().get_last_date_for_user(user_id) is None:
            date = message.text
            if validation.validate_date(date):
                to_city_id = database.Database().get_last_to_for_user(user_id)
                from_city_id = database.Database().get_last_from_for_user(user_id)

                to_city = database.Database().city_name_by_city_id(to_city_id).capitalize()
                from_city = database.Database().city_name_by_city_id(from_city_id).capitalize()

                bot.send_message(user_id, f'Давайте найдем для вас подходящий билет из {from_city} в {to_city} на {date}.')
            else:
                bot.send_message(user_id, "Вы ввели неправильный формат даты.%F0%9F%98%81")
                bot.send_message(user_id, 'Можете попробовать еще раз.')
        else:
            bot.send_message(user_id, 'Что нужно?')
bot.polling(none_stop=True)
