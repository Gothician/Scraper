# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 16:31:26 2015

@author: gothician
"""
import urllib # подключили библиотеку urllib
import lxml.html # подключили библиотеку lxml
# Открываем ГТ
page = urllib.request.urlopen("http://geektimes.ru/all")
# Получаем HTML-код главной страницы
doc = lxml.html.document_fromstring(page.read())
print(doc)
# Выбираем посты
for post in doc.cssselect('div.post'):
    print('Пост:')
    # выводим на экран название поста.
    print(post.find_class('post_title')[0].text)
    # выводим на экран текст до хабраката.
    print('Текст:')
    print(post.cssselect('div.content')[0].text)
    # выводим на экран оценку поста.
    print('Оценка: %s' % (post.find_class('score')[0].text))
    # выводим на экран автора и его рейтинг.
    rate = post.find_class('rating')
    print('Автор <%s> с рейтингом <%s>' %(rate[0].getprevious().text, rate[0].text))
    print(post.cssselect('div.content')[1].attrib)

