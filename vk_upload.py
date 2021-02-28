# -*- coding: UTF-8 -*-

import vk_api
import json
import requests
import configparser
from PySide2 import QtCore
from platform import system
from time import sleep


PLATFORM_SEP = '\\' if system() == 'Windows' else '/'  # Устанавливаем раздлитель в зависимости от ОС


class VKUpl(QtCore.QThread):
    progressBar: QtCore.SignalInstance = QtCore.Signal(object, object, object, object)
    """
         progressBar: QtCore.SignalInstance = QtCore.Signal(err_code, err_msg, iterator, msg)
    """

    def run(self):

        settings = self.read_settings()
        infile = f'temp{PLATFORM_SEP}items{PLATFORM_SEP}' + settings[0] + '.tmp'

        additional_value = settings[1]
        login = settings[2]  # _vk_login
        password = settings[3]  # _vk_password,
        group_id = settings[4]  # _group_id,

        # Выбор альбома по имени входного файла
        with open(f'configs{PLATFORM_SEP}sections', "r") as read_file:
            _sections = json.load(read_file)

        album_id = _sections[0][infile.split(f'{PLATFORM_SEP}')[-1].split('.')[0]]

        # Устанавливаем сессию в ВК
        vk_session = vk_api.VkApi(login=login, password=password,
                                  config_filename=f'configs{PLATFORM_SEP}vk_config.json')

        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            self.progressBar.emit(404, 'Не верный логин или пароль!', 0, '')
            print(error_msg)
            return

        _path = f'temp{PLATFORM_SEP}pics{PLATFORM_SEP}'
        try:
            with open(infile, "r") as read_file:
                data = json.load(read_file)

            if len(data) == 0:
                print('Товаров для загрузки в ВК нет.')
                self.progressBar.emit(404, 'Товаров для загрузки в ВК нет.', 0, '')
                return

            # print('Загружаем товары в ВК')
            len_data = len(data)
            for i in range(len_data):
                self.progressBar.emit(100, '', (i + 1) * 100 / len_data,
                                      f'Выгружено {str(i + 1)} из {str(len(data))} товаров')
                try:
                    data[i]['Цена'] = data[i]['Цена'].replace(' ', '')
                    price = (str(round(float(data[i]["Цена"]) +
                                       float(float(data[i]["Цена"]) / 100 * int(additional_value)), 2)).replace('.', ',')
                             + ' руб.' if data[i]['Цена'] != '' else 'Цена отсутствует')
                    # Формируем описание к картинке из json

                    for j in ('Название', 'Артикул', 'Размеры', 'Описание', 'Цвет', 'Материал', 'Состав'):
                        try:
                            data[i][j]
                        except KeyError:
                            data[i][j] = ''

                    description = data[i]["Название"] + '\n' + \
                        "Артикул: " + data[i]['Артикул'] + '\n' + \
                        "Цена: " + price + '\n' + \
                        (f"Размеры: {data[i]['Размеры']}\n" if data[i]['Размеры'] != '' else '') + \
                        (f"{data[i]['Описание']}\n" if data[i]['Описание'] != '' else '') + \
                        (f"Цвет: {data[i]['Цвет']}\n" if data[i]['Цвет'] != '' else '') + \
                        (f"Материал: {data[i]['Материал']}\n" if data[i]['Материал'] != '' else '') + \
                        (f"Состав: {data[i]['Состав']}" if data[i]['Состав'] != '' else '')
                except KeyError:
                    pass
                # Качаем картинку с сайта Маленького мира
                # TODO сделать проверку наличия файла картинки, есди файл скачан ранее, то пропускаем его
                img = data[i]['Картинка']
                fname = _path + img.split('/')[-1]
                p = requests.get(img)
                with open(fname, "wb") as out:
                    out.write(p.content)

                # Заливаем скачанное фото в ВК со своим описанием description='Цена: 1234 руб.',

                try:
                    upload = vk_api.VkUpload(vk_session)
                    upload.photo(
                        photos=fname,
                        album_id=album_id,
                        group_id=group_id,
                        description=description
                    )
                    sleep(0.5)
                    # self.progressBar.emit((i+1)*100/len_data, f'Выгружено {str(i+1)} из {str(len(data))} товаров')
                    print(f'Выгружено \r{str(i+1)} из {str(len(data))} товаров', end='', flush=True)
                except vk_api.exceptions.ApiError:
                    # self.progressBar.emit(404, 'В файле configs/sections не установлен id альбома')
                    # return
                    pass

            print('\nЗавершено')
            self.progressBar.emit(200, 'Завершено.', 0, '')
        except FileNotFoundError:
            self.progressBar.emit(404, f'Файл {infile} не найден.', 0, '')

    @staticmethod
    def read_settings():
        """
        Читает настройки из файла конфигурации

        :return:
        """
        try:
            vkconfig = configparser.ConfigParser()
            vkconfig.read(f'configs{PLATFORM_SEP}vkconfig')
            return [vkconfig.get('vkconfig', 'SECTION'),
                    int(vkconfig.get('vkconfig', 'ADDITIONAL_VALUE')),
                    vkconfig.get('vkconfig', 'VK_LOGIN'),
                    vkconfig.get('vkconfig', 'VK_PASSWORD'),
                    vkconfig.get('vkconfig', 'GROUP_ID')
                    ]
        except configparser.NoSectionError:
            print(f'Файл configs{PLATFORM_SEP}vkconfig не найден')

            vkconfig = configparser.ConfigParser()
            vkconfig['vkconfig'] = {
                'ADDITIONAL_VALUE': '',
                'VK_LOGIN': '',
                'VK_PASSWORD': '',
                'GROUP_ID': '',
            }
            with open(f'configs{PLATFORM_SEP}vkconfig', 'w') as configfile:
                vkconfig.write(configfile)
            return ['', '20', '', '', '']
