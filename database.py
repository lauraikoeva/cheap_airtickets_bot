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
        query = f"INSERT INTO users (user_id) VALUES ({user_id});"
        self.__query(query)
        
    def user_exist(self, user_id):
        """Проверяет существование пользователя в базе данных"""
        query = f"SELECT * FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)
        if record == []:
            return False
        return True
        
    def get_last_to_for_user(self, user_id):
        """Показывает iata города, в который пользователь искал билет в последний раз"""
        query = f"SELECT last_to FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)[0][0]
        return record

    def get_last_from_for_user(self, user_id):
        """Показывает iata города, из которого пользователь искал билет в последний раз"""
        query = f"SELECT last_from FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)[0][0]
        return record

    def get_last_date_for_user(self, user_id):
        """Показывает iata города, из которого пользователь искал билет в последний раз"""
        query = f"SELECT last_date FROM users WHERE user_id = {user_id};"
        record = self.__query(query, commit=False)[0][0]
        return record

    def set_last_to_for_user(self, user_id, city_iata):
        """Задает iata города, в который пользователь искал билет в последний раз"""
        city_iata = str(city_iata) if city_iata == "Null" else f"'{city_iata}'"
        query = f"UPDATE users SET last_to = {city_iata} WHERE user_id = {user_id};"
        self.__query(query)

    def set_last_from_for_user(self, user_id, city_iata):
        """Задает iata города, из которого пользователь искал билет в последний раз"""
        city_iata = str(city_iata) if city_iata == "Null" else f"'{city_iata}'"
        query = f"UPDATE users SET last_from = {city_iata} WHERE user_id = {user_id};"
        self.__query(query)

    def set_last_date_for_user(self, user_id, date):
        """Задает дату, на которую пользователь искал билет в последний раз"""
        date = str(date)
        query = f"UPDATE users SET last_date = {date} WHERE user_id = {user_id};"
        self.__query(query)

    #--------CITY--------#

    def city_exist(self, city_iata = None, city_name = None):
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
        query = f"SELECT name FROM cities;"
        record = self.__query(query, commit=False)
        record = [i[0].capitalize() for i in record]
        return record
    
    def city_iata_by_city_name(self, city_name):
        if not self.city_exist(city_name=city_name):
            return None
        query = f"SELECT iata FROM cities WHERE name = '{city_name}';"
        record = self.__query(query, commit=False)[0][0]
        return record

    def city_name_by_city_iata(self, city_iata):
        if not self.city_exist(city_iata=city_iata):
            return None
        query = f"SELECT name FROM cities WHERE iata = '{city_iata}';"
        record = self.__query(query, commit=False)[0][0]
        return record 