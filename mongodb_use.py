# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 16:02:09 2015

@author: gothician
"""

from pymongo import MongoClient

# Подключение к СУБД
CONNECTION = MongoClient('mongodb://localhost:27017/')

# CONNECTION.drop_database('scraper')

# Подключение к базе данных
DB = CONNECTION.scraper

# Подключение к коллекции
USERS = DB.users

print('Введите имя и возраст (для выхода введите "q")')

while(True):
    NAME = input('Введите имя: ')
    if NAME == 'q': # Выход
        break
    elif USERS.find_one({'name':NAME}): # Проверка уникальности записи
        print('Такое имя уже существует')
        continue
    AGE = int(input('Введите возраст: '))
    USERS.insert({'name':NAME, 'age':AGE})
    print(' ')

print('Пользователи')
for user in USERS.find():
    print('Имя: %s, возраст: %s' % (user['name'], user['age']))

CONNECTION.close()
