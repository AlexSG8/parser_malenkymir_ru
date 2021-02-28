# -*- coding: UTF-8 -*-

import json
import pickle
import requests
from bs4 import BeautifulSoup
import configparser
import os
import datetime
from time import time, sleep
import shutil
from PySide2 import QtCore
from platform import system
import concurrent.futures

PLATFORM_SEP = '\\' if system() == 'Windows' else '/'  # Устанавливаем раздлитель в зависимости от ОС
HTML_PARSER = 'lxml'


def read_settings():
    """
    Читает настройки из файла конфигурации

    :return: number, username, password, output_filename, dump_to_file, section_url
    """
    try:
        config = configparser.ConfigParser()
        config.read(f'configs{PLATFORM_SEP}config')

        try:
            _number = int(config.get('config', 'PRODUCT_COUNT'))
        except ValueError:
            _number = 0
        return [_number,
                config.get('config', 'USERNAME'),
                config.get('config', 'PASSWORD'),
                config.get('config', 'DUMP_TO_FILE'),
                config.get('config', 'SECTION_URL'),
                # config.get('config', 'OUTPUT_DIR'),
                ]

    except configparser.NoSectionError:
        ParserMM.progressBar.emit(500, 'Файл настроек не найден. Создаю настройки по умолчанию.\n', 0, '')
        ParserMM.write_settings(_number=80,
                                _username='',
                                _password='',
                                _dump_to_file='csv',
                                _section_url='Шапки',
                                _output_dir='output',
                                _additional_value=20,
                                _vk_login='',
                                _vk_password='',
                                _group_id='',
                                )

        ParserMM.dump_to_json(f'configs{PLATFORM_SEP}sections', {
            "Верхняя одежда": "",
            "Предзаказ": "",
            "Карнавал": "",
            "Обувь": "",
            "Распродажа": "",
            "Трикотаж": "",
            "Чулочно-носочные изделия": "",
            "Шапки": "",
            "Школа": ""
        },
                              'w')

        return [1, '', '', 'csv', 'Шапки', 'output', 20, '', '', '']


def sections():
    # ссылки на разделы каталогов
    return {
        "Верхняя одежда": "http://www.malenkymir.ru/catalog/verkhnyaya_odezhda/",
        "Карнавал": "http://www.malenkymir.ru/catalog/karnaval_1/",
        "Обувь": "http://www.malenkymir.ru/catalog/obuv_1/",
        "Распродажа": "http://www.malenkymir.ru/catalog/rasprodazha_1/",
        "Трикотаж": "http://www.malenkymir.ru/catalog/trikotazh_1/",
        "Чулочно-носочные изделия": "http://www.malenkymir.ru/catalog/chulochno_nosochnye_izdeliya/",
        "Шапки": "http://www.malenkymir.ru/catalog/shapki_4/",
        "Школа": "http://www.malenkymir.ru/catalog/shkola_7/",
    }


class ParserMM(QtCore.QThread):
    progressBar: QtCore.SignalInstance = QtCore.Signal(object, object, object, object)
    """
         progressBar: QtCore.SignalInstance = QtCore.Signal(err_code, err_msg, iterator, msg)
    """

    def authorisation(self, _username, _password):
        """
            Авторизация и сохранение cookies

            :param _username:        пользователь
            :param _password:        пароль
            :return:                status code
            """

        useragent = 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'

        link = 'http://www.malenkymir.ru/?login=yes'
        header = {
            'user-agent': useragent
        }
        data = {
            'backurl': "/",
            'AUTH_FORM': "Y",
            'TYPE': "AUTH",
            'USER_LOGIN': _username,
            'USER_PASSWORD': _password,
            'Login': '%C2%EE%E9%F2%E8',
        }

        session = requests.Session()

        try:
            # Загрузка cookies из файла
            with open(f'configs{PLATFORM_SEP}cookie', 'rb') as f:
                session.cookies.update(pickle.load(f))
        except FileNotFoundError:
            # Запись cookies в файл
            with open(f'configs{PLATFORM_SEP}cookie', 'wb') as f:
                pickle.dump(session.cookies, f)
        try:
            self.progressBar.emit(100, '', 0, 'Устанавливаю сессию')
            response = session.post(link, data=data, headers=header).reason
            self.progressBar.emit(100, 'Сессия установлена', 0, 'Устанавливаю сессию')
            sleep(0.1)
            print(response if False else '', end='')
        except Exception:
            self.progressBar.emit(500, f'Сеть не доступна. Проверьте настройки сети и нажмите "ОК"', 0, '')
            self.authorisation(_username, _password)

        return session

    def get_soup(self, url, msg, session, save_flag, *args, **kwargs):
        try:
            for i in range(5):
                try:
                    response = session.get(url, timeout=10, **kwargs)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, features=HTML_PARSER)
                    else:
                        soup = None

                    if save_flag:
                        filename = f'temp{PLATFORM_SEP}soup{PLATFORM_SEP}'\
                                   + url[25:].replace('/', '_').replace('?', '_')
                        with open(filename, 'w') as soup_temp:
                            soup_temp.write(str(soup.encode('utf-8')))
                        sleep(0.1)  # Задержка, чтобы не забанили

                    return soup

                except requests.exceptions.ReadTimeout:
                    self.progressBar.emit(600, f'Попытка подключения № {i + 2}', args, msg)
        except ConnectionError:
            self.progressBar.emit(500, f'Сеть не доступна. Проверьте настройки сети и нажмите "ОК"', args, msg)
        return 'Page not loaded'

    def crawl_products(self, _url, _pages_count, _number, session):
        """
        Собирает со страниц с 1 по pages_count включительно ссылки на товары.

        :param session:
        :param  _url:             адрес раздела каталога.
        :param  _pages_count:     количество страниц с товарами.
        :param  _number:          количество карточек товара на странице

        :return:                список URL товаров.
        """
        try:
            urls = []

            for page_n in range(1, 1 + _pages_count):
                page_url = _url + f'?action=page&number={_number}&PAGEN_1={page_n}'

                soup = self.get_soup(page_url,
                                     f'Страница {str(page_n)} из {str(_pages_count)} загружена.', session, False)

                if soup != 'Page not loaded':
                    if soup is None:
                        break

                    for tag in soup.select('.goods_grid .link_tovar'):
                        urls.append(f'http://www.malenkymir.ru{tag.attrs["href"]}')

                    self.progressBar.emit(100, '', (page_n + 1) * 100 / (_pages_count + 1),
                                          f'Страница {str(page_n)} из {str(_pages_count)} загружена.')
                else:
                    self.progressBar.emit(300, 'Не удалось загрузить страницу. Пропускаю.',
                                          (page_n + 1) * 100 / (_pages_count + 1),
                                          f'Страница {str(page_n)} из {str(_pages_count)} загружена.')

            self.progressBar.emit(100, '', 100, f'Найдено товаров: {len(urls)}')

            with open(f'temp{PLATFORM_SEP}urls.tmp', 'w') as urls_temp:
                for i in urls:
                    urls_temp.write(i + '\n')
        except Exception:
            self.progressBar.emit(404, Exception, 0, '')
        sleep(1.0)

    def parse_worker(self, url, urls_index, c, session):
        try:
            # Загружаем страницу товара с адреса url
            soup = self.get_soup(url, f'Загружаем товар {urls_index + 1} из {c}', session, True)
            if soup is None:
                return 0
            # Записываем загруженную страницу в файл
            filename = f'temp{PLATFORM_SEP}soup{PLATFORM_SEP}{"_".join(url.split("/")[3:])}'
            with open(filename, 'w') as file:
                file.write(str(soup))
            # Добавляем адрес к списку имен файлов исходников
            # data.append(filename)

            with open(f'temp{PLATFORM_SEP}soup.tmp', 'a') as soup_temp:
                soup_temp.write(filename + '\n')
            return 1
        except Exception:
            self.progressBar.emit(404, Exception, 0, '')

    def parse_products(self, infile, session, section):

        """
        Парсинг полей:
            название, цена и таблица характеристик по каждому товару.

        :param section:
        :param session:
        :param infile:          список URL на карточки товаров.
        :return:                время выполнения
        """
        try:
            with open(infile, 'r') as inf:
                f = inf.readlines()
            urls = [line.strip('\n') for line in f]
            c = str(len(urls))
            with open(f'temp{PLATFORM_SEP}soup.tmp', 'w') as soup_temp:
                soup_temp.write(section+'\n')
            result = 0

            # Берем адрес из списка и загружаем страницы в 5 потоков
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for url in urls:
                    futures.append(
                        executor.submit(
                            self.parse_worker,
                            url=url,
                            urls_index=urls.index(url),
                            c=c,
                            session=session
                        )
                    )
                for futures in concurrent.futures.as_completed(futures):
                    result += futures.result()
                    self.progressBar.emit(100, url, result * 100 / int(c),
                                          f'Загружаем товар {result} из {c}')
        except Exception:
            self.progressBar.emit(404, Exception, 0, '')

    def parse_pages(self, code):
        try:
            # Загружаем файл с именами файлов исходников
            with open(f'temp{PLATFORM_SEP}soup.tmp', 'r') as inf:
                f = inf.readlines()

            # Список загруженных имен файлов исходников
            urls = [line.strip('\n') for line in f]
            c = str(len(urls))
            data = []  # список распарсенных данных
            # Пробегаем по каждому имени файла исходника
            for url in urls[1:]:
                self.progressBar.emit(code, url, (urls.index(url) + 1) * 100 / int(c),
                                      f'Парсим данные товара {urls.index(url) + 1} из {c}')
                # Открываем файл с исходником страницы товара
                try:
                    with open(url, 'r') as sites:
                        site = sites.read()
                except FileNotFoundError:
                    continue

                # Парсим данные
                soup = BeautifulSoup(site, features=HTML_PARSER)
                if soup.text != 'Page not loaded':
                    img = 'http://www.malenkymir.ru' + soup.find('a', class_='thumb-link').get('href')

                    # Пропускаем товары без картинки
                    if img.split('/')[-1] == 'no_picture.jpg':
                        os.remove(url)
                        continue

                    name = soup.select_one('.name__tovar').text.strip()
                    try:
                        price = soup.find('div', class_="in-count-price").text.rstrip(' руб.')
                    except AttributeError:
                        # price = '0'
                        os.remove(url)
                        continue
                    full_description = soup.select_one('.tovar_block .fulldescription').text
                    specifications = self.spec_dict(soup.select_one('table.characteristics').text.strip().split('\n'))
                    section = soup.select('.bread_crumbs li a')[2].text
                    size_list = []
                    for i in soup.find_all('a', class_='size-block-el sku'):
                        size_list.append(i.text)
                    sizes = '/'.join(size_list)

                    item = {
                        'Раздел': section,
                        'Название': name,
                        'Цена': price,
                        'Размеры': sizes,
                        'Описание': full_description,
                        'URL': url,
                        'Картинка': img,
                    }
                    item.update(specifications)
                    data.append(item)
                os.remove(url)

            # Сохраняем предыдущий файл с результатами парсинга
            file_path = f'temp{PLATFORM_SEP}items{PLATFORM_SEP}{urls[0]}.tmp'
            if os.path.exists(file_path):
                shutil.move(file_path, file_path + '-' + str(int(datetime.datetime.now().timestamp())))

            self.dump_to_json(file_path, data, 'w')
        except Exception:
            self.progressBar.emit(404, Exception, 0, '')

    @staticmethod
    def spec_dict(row_col):
        """
            Преобразование таблицы характеристик в словарь

            :param row_col:         список характеристик c "пустыми" символами
                                    (Например:
                                    soup.select_one('table', class_="characteristics tbody").text..strip().split('\n')
            :return:                массив спарсенных данных по каждой из характеристик.
            """
        clear_col, specifications_dict = [], {}
        clear_col += ([i for i in row_col if not i == ''])
        for i in range(1, len(clear_col), 2):
            clear_col[i - 1] = str(clear_col[i - 1]).replace(':', '')
            specifications_dict[clear_col[i - 1]] = clear_col[i]
        return specifications_dict

    @staticmethod
    def dump_to_json(filename, data, rec_mode, **kwargs):
        """
        Записывает данные в файл json

        :param filename: Имя файла
        :param data: Данные
        :param rec_mode: Режим записи 'w'/'a'
        :param kwargs:
        """

        kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('indent', 1)

        with open(filename, rec_mode) as f:
            json.dump(data, f, **kwargs)

    def main(self, _product_count,
             _username,
             _password,
             _file_format,
             _section_url,
             ):
        """

        :param _product_count:
        :param _file_format:
        :param _username:
        :param _password:
        :param _section_url:

        :return:
        """

        # Устанавливаем сессию
        session = self.authorisation(_username, _password)
        section = sections()[_section_url]
        self.progressBar.emit(100, '', 0, f'Загружаем раздел "{_section_url}"')

        threaded_start = time()
        # Список страниц, для поиска последней
        page = []
        pages = self.get_soup(section + f'?action=page&number={_product_count}',
                                        f'Загружаем раздел "{_section_url}"', session, False)

        if pages != 'Page not loaded':
            # Выясняем последнюю страницу раздела
            pages = pages.find('ul', class_='nav-pager').find_all('a')
            for pg in pages:
                page.append(pg.text)

            # Ищем URL-адреса страниц заданного раздела
            self.crawl_products(section, int(page[-1]), _product_count, session)
            # self.crawl_products(section, 1, _product_count, session)

            # Собираем страницы товаров
            self.parse_products(f'temp{PLATFORM_SEP}urls.tmp',
                                session,
                                *(i for i in sections() if i == _section_url))
            # Парсим данные со страниц товаров
            self.parse_pages(100)
            self.progressBar.emit(200, f'Завершено\nВремя скачивания: {int(time()-threaded_start)} сек.', 0, '')
            return
        else:
            self.progressBar.emit(404, 'Сайт не отвечает', 0, '')

    def run(self):
        if self.flag:
            self.parse_pages(700)
        else:
            self.main(*read_settings())

    def __init__(self, flag, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.flag = flag
