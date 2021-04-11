import sqlite3


class Database:
    def __init__(self):
        self.__connection = sqlite3.connect('data.db')

    def __query(self, query, commit=True):
        """Создает запрос к базе данных. commit = False не сохраняет таблицу"""
        cursor = self.__connection.cursor()
        cursor.execute(query)
        if commit:
            self.__connection.commit()
        record = cursor.execute(query).fetchall()
        cursor.close()
        return record

    #--------USER--------#
    def add_user(self, user_id):
        """Добавляет пользователя в базу данных"""
        query = f"INSERT INTO users (user_id,  last_to, last_from) VALUES ({user_id}, 'MOW', 'LED');"
        self.__query(query)

    def user_exist(self, user_id):
        """Проверяет существование пользователя в базе данных"""
        query = f"SELECT * FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)
        if record == []:
            return False
        return True

    def get_last_data_for_user(self, user_id):
        """Показывает id города, в который пользователь искал билет в последний раз"""
        query = f"SELECT * FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)[0]
        answer = {"to": record[1],
                  "from": record[2],
                  "day_back": record[3],
                  "month_back": record[4],
                  "year_back": record[5],
                  "day_from": record[6],
                  "month_from": record[7],
                  "year_from": record[8]}
        return answer

    def set_last_to_for_user(self, user_id, city_iata):
        """Задает id города, в который пользователь искал билет в последний раз"""
        city_iata = str(city_iata) if city_iata == "Null" else f"'{city_iata}'"
        query = f"UPDATE users SET last_to = {city_iata} WHERE user_id = {user_id};"
        self.__query(query)

    def set_last_from_for_user(self, user_id, city_iata):
        """Задает id города, из которого пользователь искал билет в последний раз"""
        city_iata = str(city_iata) if city_iata == "Null" else f"'{city_iata}'"
        query = f"UPDATE users SET last_from = {city_iata} WHERE user_id = {user_id};"
        self.__query(query)

    def set_last_date_from_for_user(self, user_id, day=None, month=None, year=None):
        """Задает дату отправления"""
        if day is not None:
            query = f"UPDATE users SET last_day_from = {day} WHERE user_id = {user_id};"
            self.__query(query)
        if month is not None:
            query = f"UPDATE users SET last_month_from = {month} WHERE user_id = {user_id};"
            self.__query(query)
        if year is not None:
            query = f"UPDATE users SET last_year_from = {year} WHERE user_id = {user_id};"
            self.__query(query)

    def set_last_date_back_for_user(self, user_id, day=None, month=None, year=None):
        """Задает дату возвращения"""
        if day is not None:
            query = f"UPDATE users SET last_day_back = {day} WHERE user_id = {user_id};"
            self.__query(query)
        if month is not None:
            query = f"UPDATE users SET last_month_back = {month} WHERE user_id = {user_id};"
            self.__query(query)
        if year is not None:
            query = f"UPDATE users SET last_year_back = {year} WHERE user_id = {user_id};"
            self.__query(query)

    #--------CITY--------#
    def city_exist(self, city_iata=None, city_name=None):
        """Проверяет существование города в базе данных. Если указаны и city_iata и city_name поиск идет по city_iata"""
        if city_iata is not None:
            query = f"SELECT * FROM cities WHERE iata = '{city_iata}';"
        else:
            query = f"SELECT * FROM cities WHERE name = '{city_name}';"
        record = self.__query(query, commit=False)
        if record == []:
            return False
        return True

    def get_city_list(self):
        """Возвращает список городов"""
        query = "SELECT name FROM cities;"
        record = self.__query(query, commit=False)
        record = [i[0] for i in record]
        return record

    def get_cities_started_at(self, pattern):
        """Возвращает список городов начинающихся на заданную подстроку"""
        query = f"SELECT name FROM cities WHERE name LIKE ('{pattern.lower()}%')"
        record = self.__query(query, commit=False)
        return [i[0] for i in record]

    def city_iata_by_city_name(self, city_name):
        """IATA города по названию"""
        if not self.city_exist(city_name=city_name):
            return None
        query = f"SELECT iata FROM cities WHERE name = '{city_name}';"
        record = self.__query(query, commit=False)[0][0]
        return record

    def city_name_by_city_iata(self, city_iata):
        """Название города по IATA"""
        if not self.city_exist(city_iata=city_iata):
            return None
        query = f"SELECT name FROM cities WHERE iata = '{city_iata}';"
        record = self.__query(query, commit=False)[0][0]
        return record

    #--------TEMP--------#
    def add_c(self, name, iata):
        """Добавление города"""
        query = f"""INSERT INTO cities (name, iata) VALUES ("{name}", "{iata}");"""
        self.__query(query)
