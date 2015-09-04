# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:38:16 2015

@author: gothician
"""

import urllib # подключили библиотеку urllib
import lxml.html # подключили библиотеку lxml
import datetime # Подключили библиотеку datetime


# Функция парсинга страницы со списком предложений,
# возвращает список словарей с данными лотов
def parse_page(doc, page_num):
    """ Разбор страницы """
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
        result.extend(parse_page(doc , (page_num + 1)))
        return result

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
results = parse_page(doc, 1)
# Засекаем время окончания выполнения скрипта и считаем разницу
end_time = datetime.datetime.now()
delta = end_time - start_time

# Выводим результат парсинга
# Время на момент парсинга
print('Данные по состоянию на: %s \n' % (results[0]['datetime'].split('.')[0]))

# Выводим описания лотов
for result in results:
    print('Заголовок объявления: %s' % (result['header']))
    print('Номер аукциона:       %s' % (result['auction_num']))
    print('Цена купить сейчас:  %s' % (result['buy_now_price']))
    print('Цена с доставкой:    %s' % (result['delivery_price']))
    if 'bid' in result:
        print('Текущая ставка:       %s' % (result['bid']))
    print('Заканчивается через:  %s' % (result['expire_time']))
    print(result['amount'] + '\n')

# Выводим время выполнения парсинга
print('Время выполнения: %s секунд' % (delta.total_seconds()))


