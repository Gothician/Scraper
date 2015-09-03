# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:38:16 2015

@author: gothician
"""

import urllib # подключили библиотеку urllib
import lxml.html # подключили библиотеку lxml
import datetime # Подключили библиотеку datetime

# Функция разбора страницы,
# возвращает список словарей и ссылку на следующую страницу
def parse_page(page, page_num):
    """ Разбор страницы """
    result = []
    # Выбираем объявления
    for advert in doc.cssselect('article.offer'):
        post ={}
        # Считываем текст объявления.
        post['text'] = advert.cssselect('h2')[0].getchildren()[0].getchildren()[0].text
        # Считываем текущую ставку
        bids = advert.cssselect('span.bid')
        if len(bids) != 0:
            post['bid'] = bids[0].getchildren()[0].tail
        result.append(post)
    # Определяем адрес следующей страницы
    next_page_url = doc.cssselect('li.next')
    # Проверяем, есть ли следующая страница
    if next_page_url[0].attrib['class'] == 'next hidden':
        # Если ссылка скрыта, то страниц нет и возвращаем результат
        return result
    else:
        # Иначе формируем парсинг следующей страницы
        next_page = urllib.request.urlopen(full_url + "&p=" + str(page_num+1))
        result.append(next_page ,(page_num + 1))

# Открываем на Aukro
domain = "http://aukro.ua/"
# жесткие диски для ноутбуков
category = "http://aukro.ua/komplektuyushchie-dlya-noutbukov-zhestkie-diski-111288"
# исправные от 1 до 4 Гбайт
modificators = "?limit=180&a_enum[11867][2]=2&a_enum[15892][6]=6"
# Формируем полный URL
full_url = domain + category + modificators
# Открываем страницу
page = urllib.request.urlopen(full_url)
page_num = 1
# Получаем HTML-код главной страницы
doc = lxml.html.document_fromstring(page.read())
results = []

# Вызываем функцию парсинга и засекаем время
start_time = datetime.datetime.now()
results = parse_page(page, page_num)
end_time = datetime.datetime.now()
delta = end_time - start_time

# Выводим результат парсинга
for result in results:
    print('Текст объявления: %s' % (result['text']))
    if 'bid' in result:
        print('Текущая ставка: %s' % (result['bid']))
    print()

# Выводим время выполнения парсинга
print('Время выполнения: %s секунд' % (delta.total_seconds()))


