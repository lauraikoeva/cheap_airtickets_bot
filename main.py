import telebot
import datetime
from telebot import types
import database
import request

bot = telebot.TeleBot('1608185959:AAEOTN992X9fP1WFPxyvFmZKMQmIc37rmHU')


temp_user_search_back = []
show_back_date = types.InlineKeyboardButton(text="Билет в обе стороны", callback_data="show_back_date")
hide_back_date = types.InlineKeyboardButton(text="Билет в одну сторону", callback_data="hide_back_date")


def make_date_str(day, month, year):
    date = datetime.datetime.now()
    day = date.day if day is None else day
    month = date.month if month is None else month
    year = date.year if year is None else year
    month = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"][month]
    return f"{day} {month} {year}"

def make_markup(user_id, back=False):
    keyboard = types.InlineKeyboardMarkup()
    data = database.Database().get_last_data_for_user(user_id)
    city = database.Database().city_name_by_city_iata

    from_button = types.InlineKeyboardButton(text=f'{city(data["from"]).upper()}', callback_data="change_city_from")
    to_button = types.InlineKeyboardButton(text=f'{city(data["to"]).upper()}', callback_data="change_city_back")

    from_date= types.InlineKeyboardButton(text=make_date_str(data["day_from"], data["month_from"], data["year_from"]), callback_data="change_date_from")
    back_date = types.InlineKeyboardButton(text=make_date_str(data["day_back"], data["month_back"], data["year_back"]), callback_data="change_date_back")

    search = types.InlineKeyboardButton(text='Найти', callback_data="search")


    keyboard.add(from_button,to_button)
    keyboard.add(from_date)
    if back:
        keyboard.add(hide_back_date)
        keyboard.add(back_date)
    else:
        keyboard.add(show_back_date)
    keyboard.add(search)


    return keyboard

def make_years_markup(back = False):
    year = datetime.datetime.now().year

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(text=f'{year}', callback_data=f"change_month_back {year}" if back else f"change_month_from {year}"))
    keyboard.add(types.InlineKeyboardButton(text=f'{year+1}', callback_data=f"change_month_back {year+1}" if back else f"change_month_from {year+1}"))

    return keyboard

def make_months_markup(back = False):
    keyboard = types.InlineKeyboardMarkup()
    months = ["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    for m in range(0,12,2):
        keyboard.add(types.InlineKeyboardButton(text=months[m], callback_data=f"change_day_back {m}" if back else f"change_day_from {m}"),
                        types.InlineKeyboardButton(text=months[m+1], callback_data=f"change_day_back {m+1}" if back else f"change_day_from {m+1}"))

    return keyboard

def make_days_markup(month:int, year:int, back = False):
    keyboard = types.InlineKeyboardMarkup()
    day = 31
    if month in [4, 6, 9, 11]:
        day = 30
    if month == 2:
        day = 29
    if month == 2 and year % 4 == 0 and year % 100 != 0:
        day = 28
    line = []
    for d in range(1, day+1):
        if (d-1)%3==0:
            keyboard.add(*line)
            line=[]
        line.append(types.InlineKeyboardButton(text=f"{d}", callback_data=f"date_back_changed {d}" if back else f"date_from_changed {d}"))
    if line != []:
        keyboard.add(*line)

    return keyboard

def make_keyboard(pattern, back):
    cities = [city for city in database.Database().get_city_list() if city[:len(pattern)] == pattern]

    keyboard = types.InlineKeyboardMarkup()

    if pattern in cities:
        if back:
            iata = database.Database().city_iata_by_city_name(pattern)
            keyboard.add(types.InlineKeyboardButton(text=pattern.upper(), callback_data=f"change_city_{'back' if back else 'from'}_to {iata}"))
        cities.remove(pattern)

    if len(cities) > 14:
        keys = sorted(list(set([i[len(pattern)] for i in cities])))
        line = []
        for key in keys:
            if len(line) > 5:
                keyboard.add(*line)
                line=[]
            line.append(types.InlineKeyboardButton(text=key.upper(), callback_data=f"change_city_{'back' if back else 'from'} {pattern + key}"))
        if line != []:
            keyboard.add(*line)
    else:
        for city in cities:
            iata = database.Database().city_iata_by_city_name(city)
            keyboard.add(types.InlineKeyboardButton(text=city.upper(), callback_data=f"change_city_{'back' if back else 'from'}_to {iata}"))
    
    if len(pattern) > 0:
        keyboard.add(types.InlineKeyboardButton(text="<<", callback_data=f"change_city_{'back' if back else 'from'} {pattern[:-1]}"))

    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    """Запуск чата с ботом"""
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Найти билет')
    bot.send_message(
        message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Я бот, который найдет "САМЫЙ" дешевый авиабилет для Вас.', reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def start_message(message):
    if message.text.lower() != "найти билет":
        bot.send_message(message.chat.id, "Чтобы найти билет, введите 'Найти билет'")
        return None

    user_id = message.from_user.id
    if not database.Database().user_exist(user_id):
        database.Database().add_user(user_id)

    date = datetime.datetime.now() + datetime.timedelta(1)

    if user_id in temp_user_search_back:
        temp_user_search_back.remove(user_id)
    
    database.Database().set_last_date_from_for_user(user_id, date.day, date.month-1, date.year)
    database.Database().set_last_date_back_for_user(user_id, date.day, (date.month)%12, date.year)

    keyboard = make_markup(user_id)

    bot.send_message(message.chat.id, "Параметры поиска:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print(call.data)
    user_id = call.from_user.id
    back = False
    if user_id in temp_user_search_back:
        back = True
    if call.message:
        call_data = call.data.split()
        if call_data[0] == "change_city_from":
            if len(call_data) == 1:
                call_data.append("")
            keyboard = make_keyboard(call_data[1], False)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Новый город отправления: "+call_data[1].upper(), reply_markup=keyboard)
        
        if call_data[0] == "change_city_from_to":
            database.Database().set_last_from_for_user(user_id, call_data[1].upper())
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти билет", reply_markup=make_markup(user_id,back=back))

        if call_data[0] == "change_city_back":
            if len(call_data) == 1:
                call_data.append("")
            keyboard = make_keyboard(call_data[1], True)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Новый город назначения: "+call_data[1].upper(), reply_markup=keyboard)
        

        if call_data[0] == "change_city_back_to":
            database.Database().set_last_to_for_user(user_id, call_data[1].upper())
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти билет", reply_markup=make_markup(user_id,back=back))


        if call_data[0] == "change_day_from":
            database.Database().set_last_date_from_for_user(user_id, month=int(call_data[1]))
            data = database.Database().get_last_data_for_user(user_id)
            month = data["month_from"]
            year = data["year_from"]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый день отправления", reply_markup=make_days_markup(month,year))

        if call_data[0] == "change_month_from":
            database.Database().set_last_date_from_for_user(user_id, year=int(call_data[1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый месяц отправления", reply_markup=make_months_markup())

        if call_data[0] == "change_date_from":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый год отправления", reply_markup=make_years_markup())

        if call_data[0] == "change_day_back":
            database.Database().set_last_date_back_for_user(user_id, month=int(call_data[1]))
            data = database.Database().get_last_data_for_user(user_id)
            month = data["month_back"]
            year = data["year_back"]
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый день возвращения", reply_markup=make_days_markup(month,year, back=True))

        if call_data[0] == "change_month_back":
            database.Database().set_last_date_back_for_user(user_id, year=int(call_data[1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый месяц возвращения", reply_markup=make_months_markup(back=True))

        if call_data[0] == "change_date_back":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите новый год возвращения", reply_markup=make_years_markup(back=True))

        if call_data[0] == "date_from_changed":
            database.Database().set_last_date_from_for_user(user_id, day=int(call_data[1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти билет", reply_markup=make_markup(user_id,back=back))
            
        if call_data[0] == "date_back_changed":
            database.Database().set_last_date_back_for_user(user_id, day=int(call_data[1]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти билет", reply_markup=make_markup(user_id,back=back))
            
        if call_data[0] == "search":
            months = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
            text = ""
            data = database.Database().get_last_data_for_user(user_id)

            data['day_from'] = "0" + str(data['day_from']) if int(data['day_from']) < 9 else data['day_from']
            data['month_from'] += 1
            data['month_from'] = "0" + str(data['month_from']) if int(data['month_from']) < 9 else data['month_from']
            data['day_back'] = "0" + str(data['day_back']) if int(data['day_back']) < 9 else data['day_back']
            data['month_back'] += 1
            data['month_back'] = "0" + str(data['month_back']) if int(data['month_back']) < 9 else data['month_back']

            c_from = database.Database().city_name_by_city_iata(data["from"]).upper()
            c_to = database.Database().city_name_by_city_iata(data["to"]).upper()

            text += f'''Билет {c_from} -> {c_to}\n\n'''
            text += f'''Отправление:\n{data["day_from"]} {months[int(data["month_from"])-1]} {data["year_from"]}\n'''

            ticket = request.search(data["from"], data["to"], f"{data['day_from']}.{data['month_from']}.{data['year_from']}")
            if ticket is False:
                text += "Не найден"
            else:
                text += f'''Стоит {ticket["value"]}р. {ticket["gate"]}'''

            if user_id in temp_user_search_back:
                text += f'''\n\nОбратный билет:\n{data["day_back"]} {months[int(data["month_back"])-1]} {data["year_back"]}\n'''
                ticket = request.search(data["to"], data["from"], f"{data['day_back']}.{data['month_back']}.{data['year_back']}")
                if ticket is False:
                    text += "Не найден"
                else:
                    text += f'''Стоит {ticket["value"]}р. {ticket["gate"]}'''

                temp_user_search_back.remove(user_id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text)

        if call_data[0] == "show_back_date":
            if user_id not in temp_user_search_back:
                temp_user_search_back.append(user_id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Заполните данные для возвращения", reply_markup=make_markup(user_id,back=True))

        if call_data[0] == "hide_back_date":
            if user_id in temp_user_search_back:
                temp_user_search_back.remove(user_id)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Найти билет",reply_markup=make_markup(user_id))


if __name__ == "__main__":
    bot.polling(none_stop=True)
