# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:38:16 2015

@author: gothician
"""

import sys # Подключаем библиотеку для получения строки параметров
import urllib.request # подключили библиотеку для запросов по сети
import lxml.html # подключили библиотеку для разбора страниц
import datetime # Подключили библиотеку для работы со временем
from pymongo import MongoClient # Импортируем функционал для подключения к БД
import re # Импортируем библиотеку для работы с регулярными выражениями
from os import makedirs as makedir # Импортируем функцию создания директории

# Функция вывода содержимого хелп-файла
def print_help():
    """ Help output function """
    print("""\nParsers usage:

python3 parser_[x].py [option] [-s:date] [-e:date]

Options:
-h or --help : Help
-co          : Output results on console
-fo          : Output results to file /aukro_output/aucro_data_YYYY-MM-DD:hh-mm
-wdb         : Output results to database
-rdbco       : Read results fom database and output to console
               (optionally filtered by date, date format: YYYY-MM-DD)
-rdbfo       : Read results fom database and output to file
               (optionally filtered by date, date format: YYYY-MM-DD)
-clrdb       : Clear database\n""")


# Функция вывода данных в консоль

def console_output(results, delta = None):
    """ Console output function """
    # Выводим начальное время
    start_datetime = min(result['datetime'] for result in results)
    print('Данные по состоянию на: %s' % (start_datetime.split('.')[0]))
    # Выводим описания лотов
    for result in results:
        print('\nЗаголовок объявления: %s' % (result['header']))
        print('Номер аукциона:       %s' % (result['auction_num']))
        print('Цена купить сейчас:  %s' % (result['buy_now_price']))
        print('Цена с доставкой:    %s' % (result['delivery_price']))
        if result['bid'] != None: # Если есть ставки
            print('Текущая ставка:       %s' % (result['bid']))
        print('Заканчивается через:  %s' % (result['expire_time']))
        print(result['amount'])
    # Выводим время выполнения парсинга
    if delta != None:
        print('\nВремя выполнения: %s секунд\n' % (delta.total_seconds()))


# Функция вывода данных в файл

def file_output(results, delta = None):
    """ File output function """
    # Определяем начальное время
    start_datetime = min(result['datetime'] for result in results)
    # Создаем имя файла с фиксацией времени на момент парсинга
    filename = './scraper_results/aukro_results' + '-' + (
                start_datetime.split()[0] + '_' + (
                start_datetime.split()[1][:5]))
    try: # Пытаемся открыть файл на запись
        file = open(filename, 'w')
    except FileNotFoundError: # Если нет директории запрос на ее создание
        if input("Directory 'scraper_results' don't exist. Create? y/n:"
                  ).lower() == 'y':
            makedir('./scraper_results')
            file = open(filename, 'w')
        else:
            print("Can't open file %s" % (filename))
            return -1
    # Выводим начальное время
    file.write('Данные по состоянию на: %s\n' % (start_datetime.split('.')[0]))
    # Выводим описания лотов
    for result in results:
        file.write('\nЗаголовок объявления: %s\n' % (result['header']))
        file.write('Номер аукциона:       %s\n' % (result['auction_num']))
        file.write('Цена купить сейчас:  %s\n' % (result['buy_now_price']))
        file.write('Цена с доставкой:    %s\n' % (result['delivery_price']))
        if result['bid'] != None:
            file.write('Текущая ставка:       %s\n' % (result['bid']))
        file.write('Заканчивается через:  %s\n' % (result['expire_time']))
        file.write('%s\n' % (result['amount']))
    # Выводим время выполнения парсинга
    if delta != None:
        file.write('\nВремя выполнения: %s секунд\n' % (delta.total_seconds()))
    file.close()
    # Выбираем форму вывода
    records_num = len(results)
    last_digit = records_num % 10
    if last_digit in [0, 5, 6, 7, 8, 9]:
        print('Сделано %d записей в файл %s' % (records_num, filename))
    elif last_digit in [2, 3, 4]:
        print('Сделано %d записи в файл %s' % (records_num, filename))
    else:
        print('Сделанa %d запись в файл %s' % (records_num, filename))


# Функция проверки даты
#(дописать верификацию даты)
def check_date(start_date, end_date):
    """ Date check function """
    # Проверяем вхождение месяца и числа в диапазон во внутренней функции
    def check_month_day(splitted):
        if ('01' <= splitted[1] <= '12') and ('01' <= splitted[2] <= '31'):
            return True
        return False

    # Основной код функции
    if start_date != None: # Проверяем наличие начальной даты
        start_split = start_date.split('-')
    if end_date != None: # Проверяем наличие конечной даты
        end_split = end_date.split('-')
    if start_date == None: # Проверяем конечную, если нет начальной
        return check_month_day(end_split)
    elif end_date == None: # Проверяем начальную, если нет конечной
        return check_month_day(start_split)
    elif start_date <= end_date: # Проверяем обе
        if  check_month_day(start_split) and check_month_day(end_split):
            return True
    return False # Если не прошла проверка


# Функция разбора аргументов

def parse_args(args):
    """ Arguments parse finction """
    # При вызове без параметров выводим справку
    if len(args) == 1:
        return ('help', None, None)
    # Проверяем, что первый параметр соответствует командам
    elif args[1] in ['-co', '-fo', '-wdb', '-clrdb']:
        return (args[1], None, None)
    elif args[1] in ['-rdbco', '-rdbfo']: # Для чтения из базы
        date_regex = re.compile('-[s,e]:\d{4}-\d{2}-\d{2}')
        if len(args) == 2: # Если только команда, то возвращаем ее
            return (args[1], None, None)
        # Если с командой одно условие
        elif (len(args) == 3) and (date_regex.match(args[2]) != None):
            first_condition = args[2].split(':')
            if (first_condition[0] == '-s') and check_date(first_condition[1],
                None):
                return (args[1], first_condition[1], None)
            elif check_date(None, first_condition[1]):
                return (args[1], None, first_condition[1])
        elif (date_regex.match(args[2]) != None) and (date_regex.match(
               args[3]) != None): # Если с командой больше одного условия
            first_condition = args[2].split(':')
            second_condition = args[3].split(':')
            if (first_condition[0] == '-s') and (second_condition[0] == '-e'
                ) and check_date(first_condition[1], second_condition[1]):
                return (args[1], first_condition[1], second_condition[1])
            elif (first_condition[0] == '-e') and (second_condition[0] == '-s'
                  ) and check_date(second_condition[1], first_condition[1]):
                return (args[1], second_condition[1], first_condition[1])
    # Если что-то пошло не так или вызвана справка - выводим справку
    else:
        return ('help', None, None)


# функция подключения к базе данных

def db_connect(query = 'collection'):
    """ Database connect function """
    # Подключение к СУБД
    connection = MongoClient('mongodb://localhost:27017/')
    if query == 'connection':
        return connection
    # Подключение к базе данных
    db = connection.scraper_aukro
    # Подключение к коллекции
    aukro_collection = db.aukro_collection
    return aukro_collection


# Функция чтения из базы данных

def db_read(aukro_collection, interval = (None, None)):
    """ Database read function """
    start_date = interval[0]
    end_date = interval[1]
    result = []
    if start_date == None and end_date == None: # Если даты не заданы
        for data in aukro_collection.find():
            result.append(data)
    else: # Если задана хотя бы одна дата
        if start_date == None: # Присваиваем заведомо маленькое
            start_date == '1990-01-01'
        if end_date == None: # Присваиваем текущее
            end_date = datetime.datetime.now().isoformat().split(' ')[0]
        for data in aukro_collection.find():
            data_date = data['datetime'].split(' ')[0]
            if start_date <= data_date <= end_date: # Выводим в интервале
                result.append(data)
    return result


# Функция записи в базу данных

def db_write(aukro_collection, data):
    """ Database write function """
    auction_nums = [] # Создаем список уникальных идентификаторов аукционов
    for collection_data in aukro_collection.find():
        auction_nums.append(collection_data['auction_num'])
    for record in data:
        if record['auction_num'] in auction_nums: # Если запись есть - меняем
            aukro_collection.update({'auction_num': record['auction_num']},
                           {'$set': {'datetime': record['datetime'],
                                     'header': record['header'],
                                     'ref': record['ref'],
                                     'expire_time': record['expire_time'],
                                     'amount': record['amount'],
                                     'bid': record['bid']}})
        else: # Если записи нет - добавляем
            aukro_collection.insert({'datetime': record['datetime'],
                                     'header': record['header'],
                                     'ref': record['ref'],
                                     'auction_num': record['auction_num'],
                                     'buy_now_price': record['buy_now_price'],
                                     'delivery_price': record['delivery_price'],
                                     'expire_time': record['expire_time'],
                                     'amount': record['amount'],
                                     'bid': record['bid']})


# Функция очистки базы данных

def db_clear(connection):
    """ Database clear function """
    connection.drop_database('scraper_aukro')


# Функция сбора данных

def collect_data():
    """ Data collecting from site function """
    # Открываем на Aukro
    domain = "http://aukro.ua"
    # жесткие диски для ноутбуков
    category = "/komplektuyushchie-dlya-noutbukov-zhestkie-diski-111288"
    # исправные от 1 до 4 Гбайт, вывод 180 объявлений на странице
    modificators = "?limit=180&a_enum[11867][2]=2&a_enum[15892][6]=6"
    # Формируем полный URL
    full_url = domain + category + modificators
    # Открываем страницу
    request_obj = urllib.request.Request(full_url,
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'})
    page = urllib.request.urlopen(request_obj)
    # Получаем HTML-код главной страницы
    doc = lxml.html.document_fromstring(page.read())
    results = []
    # Засекаем время начала выполнения скрипта
    start_time = datetime.datetime.now()
    # Вызываем функцию парсинга с первой страницы
    results = parse_page(doc, domain, full_url, 1)
    # Засекаем время окончания выполнения скрипта и считаем разницу
    end_time = datetime.datetime.now()
    delta = end_time - start_time
    return (results, delta)


# Функция парсинга страницы со списком предложений,
# возвращает список словарей с данными лотов

def parse_page(doc, domain, full_url,  page_num):
    """ Page parsing function """
    result = []
    # Устанавливаем текущее время
    cur_datetime = datetime.datetime.now().isoformat(' ')
    # Выбираем объявления
    for advert in doc.cssselect('article.offer'):
        post = {}
        # Устанавливаем текущие данные даты и времени для поста
        post['datetime'] = cur_datetime
        header = advert.cssselect('h2')[0].getchildren()[0]
        # Считываемx текст объявления.
        post['header'] = header.getchildren()[0].text
        # Считываем ссылку
        post['ref'] = domain + header.attrib['href']
        # Выбираем номер аукциона
        post['auction_num'] = post['ref'].split('-')[-1][1:-6]
        # Считываем цену купить сейчас
        post['buy_now_price'] = advert.cssselect('span.buy-now'
                                                  )[0].getchildren()[0].tail
        # Считываем цену с доставкой
        post['delivery_price'] = advert.cssselect('span.delivery'
                                                   )[0].getchildren()[0].tail
        # Считываем время до конца
        post['expire_time'] = advert.cssselect('div.expiry'
                                  )[0].getchildren()[0].getchildren()[0].text
        # Считываем количество лотов
        amount = advert.cssselect('div.amount')[0].getchildren()[0].getchildren()
        post['amount'] = amount[0].text + ' ' + amount[1].text + amount[1].tail
        # Считываем текущую ставку
        bids = advert.cssselect('span.bid')
        if len(bids) != 0:
            post['bid'] = bids[0].getchildren()[0].tail
        else:
            post['bid'] = None
        result.append(post)
    # Определяем адрес следующей страницы
    next_page_url = doc.cssselect('li.next')
    # Проверяем, есть ли следующая страница
    if next_page_url[0].attrib['class'] == 'next hidden':
        # Если ссылка скрыта, то страниц нет и возвращаем результат
        return result
    else:
        # Иначе формируем парсинг следующей страницы
        request_obj = urllib.request.Request(full_url + "&p=" + str(page_num+1),
                        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'})
        next_page = urllib.request.urlopen(request_obj)
        doc = lxml.html.document_fromstring(next_page.read())
        result.extend(parse_page(doc , domain, full_url, (page_num + 1)))
        return result


# Логика при запуске файла
if __name__ == "__main__":

    # Разбор параметров, возвращается кортеж, где 1 элемент - команда,
    # 2 элемент - начальная дата/время, 3 элемент - конечнная дата/время
    args_tuple = parse_args(sys.argv)
    # Вывод содержимого хелп-файла при вызове программы без параметров,
    # с неправильными параметрами или с ключами -h, --help
    if args_tuple == None or args_tuple[0] == '--help':
        print_help()
    # Вывод на экран собранных данных
    elif args_tuple[0] == '-co':
        data = collect_data()
        console_output(data[0], data[1])
    # Вывод в файл собранных данных
    elif args_tuple[0] == '-fo':
        data = collect_data()
        file_output(data[0], data[1])
    # Запись в базу собранных данных
    elif args_tuple[0] == '-wdb':
        db_write(db_connect(), collect_data()[0])
    # Чтение данных из базы
    elif args_tuple[0] == '-rdbco': # Вывод в консоль данных из базы
         console_output(db_read(db_connect(), args_tuple[1:3]))
    elif args_tuple[0] == '-rdbfo': # Вывод в файл данных из базы
         file_output(db_read(db_connect(), args_tuple[1:3]))
    # Очистка базы данных
    elif args_tuple[0] == '-clrdb':
        db_clear(db_connect('connection'))
    # Вывод содержимого хелп-файла, если ввод был некорректным
    else:
        print_help()