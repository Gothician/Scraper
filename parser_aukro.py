# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:38:16 2015

@author: gothician
"""

import urllib # подключили библиотеку urllib
import lxml.html # подключили библиотеку lxml
# Открываем на Aukro жесткие диски исправные от 1 до 4 Гбайт
page = urllib.request.urlopen("http://aukro.ua/komplektuyushchie-dlya-noutbukov-zhestkie-diski-111288?limit=180&a_enum[11867][2]=2&a_enum[15892][6]=6")
# Получаем HTML-код главной страницы
doc = lxml.html.document_fromstring(page.read())
# Выбираем объявления
for advert in doc.cssselect('article.offer'):
    # Считываем текст объявления.
    text = advert.cssselect('h2')[0].getchildren()[0].getchildren()[0].text
    print('Текст: %s' % (text))
    bids = advert.cssselect('span.bid')
    if len(bids) != 0:
        print('Текущая ставка: %s' % (bids[0].getchildren()[0].tail))

    print()
