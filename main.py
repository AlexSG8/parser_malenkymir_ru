# -*- coding: utf-8 -*-
# import sys
from configparser import ConfigParser
from PySide2 import QtWidgets
from PySide2.QtWidgets import QFileDialog
import xlsxwriter
import csv
import mm_parse_gui
import progress_gui
from vk_upload import *
from mm_parser import *
import json
import configparser
import sys
import os
from platform import system
import shutil


PLATFORM_SEP = '\\' if system() == 'Windows' else '/'  # Устанавливаем раздлитель в зависимости от ОС
OLD_DATA = False


class Parse(QtWidgets.QDialog, progress_gui.UiProgress):
    def __init__(self):
        self.worker = None
        super(Parse, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Парсинг.')
        self.run()

    def run(self):
        self.worker = ParserMM(OLD_DATA)
        self.progressBar.setRange(1, 100)
        self.progressBar.setValue(0)
        self.worker.progressBar.connect(self.update_progress)
        self.worker.start()

    # def closeEvent(self, *args):
    #     # self.worker.join()
    #     # self.worker.wait()
    #     # self.worker.terminate()
    #     print('sss')

    def update_progress(self, err_code, err_msg, i, msg):

        """
        изменение label и progressBar
        :param err_code:100  - value прогрессьбара
                        200     - удачное завершение
                        404     - ошибка
                        500     - не критическая ошибка, программа не прерывается
                        600     - дополнение к выводу, например, "Попытка подключения № 2"
                        700     - установка заголовка окна прогресса
        :param err_msg: Сообщение об ошибке из сигнала
        :param i:       счетчик для прогрессбара
        :param msg:     сообщение из потока
        :return:
        """
        if err_code == 200:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            global OLD_DATA
            OLD_DATA = False
            self.hide()
        elif err_code == 300:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)

        elif err_code == 404:
            self.hide()
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr(err_msg),
                                           QtWidgets.QMessageBox.StandardButton.Ok)
        elif err_code == 500:
            QtWidgets.QMessageBox.information(None, self.tr('Парсинг.'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)
        elif err_code == 600:
            self.worker.progressBar.connect(self.error_label.setText(err_msg))
        elif err_code == 700:
            self.worker.progressBar.connect(self.error_label.setText(err_msg))
            self.setWindowTitle('Парсим данные с предыдущей сессии')
        else:
            self.worker.progressBar.connect(self.progressBar.setValue(i))
            self.error_label.setText(err_msg)
        self.label.setText(msg)


class VKUpload(QtWidgets.QDialog, progress_gui.UiProgress):
    def __init__(self):
        self.worker = None
        super(VKUpload, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Выгрузка в ВК.')
        self.run()

    def run(self):
        self.worker = VKUpl()
        self.progressBar.setRange(1, 100)
        self.progressBar.setValue(0)
        self.worker.progressBar.connect(self.update_progress)
        self.worker.start()

    def update_progress(self, err_code, err_msg, i, msg):
        """
        изменение label и progressBar

        :param err_code: до 100  - value прогрессьбара
                        200     - удачное завершение
                        404     - ошибка
        :param err_msg: Сообщение об ошибке из сигнала
        :param i:
        :param msg:     сообщение из потока
        :return:
        """
        if err_code == 200:
            QtWidgets.QMessageBox.information(None, self.tr('Выгрузка в ВК'),
                                              self.tr(err_msg),
                                              QtWidgets.QMessageBox.StandardButton.Ok)
            self.hide()
        elif err_code == 404:
            self.hide()
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr(err_msg),
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            self.hide()
        else:
            self.worker.progressBar.connect(self.progressBar.setValue(i))
        self.label.setText(msg)


class MainWindow(QtWidgets.QMainWindow, mm_parse_gui.Ui_MainWindow):
    def openParseDialog(self):
        self.write_settings()
        self.w1 = Parse()
        self.w1.show()

    def openVKUpload(self):
        self.write_vk_settings()
        self.w2 = VKUpload()
        self.w2.show()

    def change_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        self.output_dir_entry.setText(directory)

    @staticmethod
    def _save_file(_section_url):
        file = QFileDialog.getSaveFileName(filter='*.xlsx;; *.csv;; *.json')
        save_file(file[0], file[1].replace('*.', ''), f'temp{PLATFORM_SEP}items{PLATFORM_SEP}{_section_url}.tmp')

    def __init__(self):
        self.w1, self.w2 = None, None
        super().__init__()
        self.setupUi(self)

        self.fill_parser_settings_fields()  # Заполняем поля ввода значениями из configs/config
        self.fill_vk_upload_fields()  # Заполняем поля ввода значениями из configs/vkconfig
        self.parse_button.pressed.connect(self.openParseDialog)
        self.vk_upload_button.pressed.connect(self.openVKUpload)
        section = self.section_combo.currentText()
        self.save_as.triggered.connect(lambda: self._save_file(section))

        tmp_dir = os.listdir(f'temp{PLATFORM_SEP}soup')
        if len(tmp_dir) != 0:
            p = QtWidgets.QMessageBox.question(None, self.tr('Парсинг.'),
                                               'С прошлого запуска остались не распарсенные данные.\n'
                                               ' Распарсить их?',
                                               QtWidgets.QMessageBox.StandardButton.Yes,
                                               QtWidgets.QMessageBox.StandardButton.No)
            if p == QtWidgets.QMessageBox.Yes:
                global OLD_DATA
                OLD_DATA = True
                self.openParseDialog()
            else:
                OLD_DATA = False
                shutil.rmtree(f'temp{PLATFORM_SEP}soup')
                os.mkdir(f'temp{PLATFORM_SEP}soup')

    def write_settings(self):

        config = configparser.ConfigParser()
        config['config'] = {
            'PRODUCT_COUNT': '80',
            'USERNAME': self.username_entry.text(),
            'PASSWORD': self.password_entry.text(),
            'DUMP_TO_FILE': 'csv',
            'SECTION_URL': self.section_combo.currentText(),
        }

        with open(f'configs{PLATFORM_SEP}config', 'w') as configfile:
            config.write(configfile)

    def write_vk_settings(self):

        config = configparser.ConfigParser()
        config['vkconfig'] = {
            'ADDITIONAL_VALUE': self.additional_value_entry.text(),
            'VK_LOGIN': self.vk_login_entry.text(),
            'VK_PASSWORD': self.vk_password_entry.text(),
            'GROUP_ID': self.group_id_entry.text(),
            'SECTION': self.section_combo_vk.currentText(),
        }

        with open(f'configs{PLATFORM_SEP}vkconfig', 'w') as configfile:
            config.write(configfile)

    def fill_parser_settings_fields(self):
        try:
            config: ConfigParser = configparser.ConfigParser()
            config.read(f'configs{PLATFORM_SEP}config')

            try:
                with open(f'configs{PLATFORM_SEP}sections', 'r') as file:
                    json.load(file)
            except FileNotFoundError:
                QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                               self.tr('Файл настроек разделов сайта не найден...'),
                                               QtWidgets.QMessageBox.StandardButton.Ok)
            finally:
                with open(f'configs{PLATFORM_SEP}sections', 'r') as file:
                    sections_from_file = json.load(file)
            count = 0
            for i in dict(sections_from_file[0]).keys():
                self.section_combo.addItem("")
                self.section_combo.setItemText(count, i)
                count += 1

            self.username_entry.setText(config.get('config', 'USERNAME'))
            self.password_entry.setText(config.get('config', 'PASSWORD'))
            self.section_combo.setCurrentText(config.get('config', 'SECTION_URL'))

        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr('Файл настроек парсера не найден...'),
                                           QtWidgets.QMessageBox.StandardButton.Ok)

    def fill_vk_upload_fields(self):
        try:
            config: ConfigParser = configparser.ConfigParser()
            config.read(f'configs{PLATFORM_SEP}vkconfig')
            try:
                with open(f'configs{PLATFORM_SEP}sections', 'r') as file:
                    json.load(file)
            except FileNotFoundError:
                QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                               self.tr('Файл настроек разделов сайта не найден...'),
                                               QtWidgets.QMessageBox.StandardButton.Ok)
            finally:
                with open(f'configs{PLATFORM_SEP}sections', 'r') as file:
                    sections_from_file = json.load(file)
            count = 0
            for i in dict(sections_from_file[0]).keys():
                self.section_combo_vk.addItem("")
                self.section_combo_vk.setItemText(count, i)
                count += 1

            self.additional_value_entry.setText(config.get('vkconfig', 'ADDITIONAL_VALUE'))
            self.vk_login_entry.setText(config.get('vkconfig', 'VK_LOGIN'))
            self.vk_password_entry.setText(config.get('vkconfig', 'VK_PASSWORD'))
            self.group_id_entry.setText(config.get('vkconfig', 'GROUP_ID'))

        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(None, self.tr('Ошибка!'),
                                           self.tr('Файл настроек ВК не найден...'),
                                           QtWidgets.QMessageBox.StandardButton.Ok)


def main():
    try:
        os.mkdir('configs')
    except FileExistsError:
        pass
    try:
        with open(f'configs{PLATFORM_SEP}config', 'r') as file:
            file.read()
    except FileNotFoundError:
        config = configparser.ConfigParser()
        config['config'] = {
            'PRODUCT_COUNT': '80',
            'USERNAME': '',
            'PASSWORD': '',
            'DUMP_TO_FILE': 'json',
            'SECTION_URL': 'Шапки',
        }
        with open(f'configs{PLATFORM_SEP}config', 'w') as configfile:
            config.write(configfile)

    try:
        with open(f'configs{PLATFORM_SEP}sections', 'r') as file:
            file.read()
    except FileNotFoundError:
        ParserMM.dump_to_json(None, [{
            "Верхняя одежда": "",
            "Предзаказ": "",
            "Карнавал": "",
            "Обувь": "",
            "Распродажа": "",
            "Трикотаж": "",
            "Чулочно-носочные изделия": "",
            "Шапки": "",
            "Школа": ""
        }],
            'w')

    try:
        with open(f'configs{PLATFORM_SEP}vkconfig', 'r') as file:
            file.read()
    except FileNotFoundError:
        config = configparser.ConfigParser()
        config['vkconfig'] = {
            'ADDITIONAL_VALUE': '',
            'VK_LOGIN': '',
            'VK_PASSWORD': '',
            'GROUP_ID': '',
        }

        with open(f'configs{PLATFORM_SEP}vkconfig', 'w') as configfile:
            config.write(configfile)

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def save_file(_filename, _format, _data):
    if _format == 'csv':
        dump_to_csv(_filename + '.' + _format, _data)
    elif _format == 'xlsx':
        dump_to_xlsx(_filename + '.' + _format, _data)
    elif _format == 'json':
        shutil.copy2(_data, _filename + '.' + _format)


def dump_to_xlsx(filename, infile):
    """
    Записывает данные в файл Excel

    :param  filename:       имя файла для записи.
    :param  infile:         данные для записи.
    :return:                None, если данных для записи нет.
    """
    if not len(infile):
        return None

    try:
        with open(infile, "r"):
            pass
    except FileNotFoundError:
        with open(infile, 'w'):
            pass
    finally:
        with open(infile, "r") as read_file:
            data = json.load(read_file)

    with xlsxwriter.Workbook(filename) as workbook:
        ws = workbook.add_worksheet()
        cell_format_bottom = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'left',
            'font_size': 10
        })
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'font_size': 10
        })

        headers = ['Раздел', 'Артикул', 'Наименование', 'Цена', 'Размер', 'Цвет', 'Фото', 'Описание']

        for col, h in enumerate(headers):
            ws.write_string(0, col, h, cell_format=cell_format_bottom)

        for row, item in enumerate(data, start=1):
            try:
                item['Раздел']
            except KeyError:
                item['Раздел'] = ''
            try:
                item['Артикул']
            except KeyError:
                item['Артикул'] = ''
            try:
                item['Название']
            except KeyError:
                item['Название'] = ''
            try:
                item['Цена']
            except KeyError:
                item['Цена'] = ''
            try:
                item['Размеры']
            except KeyError:
                item['Размеры'] = ''
            try:
                item['Цвет']
            except KeyError:
                item['Цвет'] = ''
            try:
                item['Картинка']
            except KeyError:
                item['Картинка'] = ''
            try:
                item['Описание']
            except KeyError:
                item['Описание'] = ''

            ws.write_string(row, 0, item['Раздел'], cell_format=cell_format)
            ws.write_string(row, 1, item['Артикул'], cell_format=cell_format)
            ws.write_string(row, 2, item['Название'], cell_format=cell_format)
            ws.write_string(row, 3, item['Цена'], cell_format=cell_format)
            ws.write_string(row, 4, item['Размеры'], cell_format=cell_format)
            ws.write_string(row, 5, item['Цвет'], cell_format=cell_format)
            ws.write_string(row, 6, item['Картинка'], cell_format=cell_format)
            ws.write_string(row, 7, item['Описание'], cell_format=cell_format)


def dump_to_csv(filename, infile, delimiter=';'):
    """
    Записывает данные в файл .csv

    :param  filename:       имя файла для записи.
    :param  infile:         данные для записи.
    :param  delimiter:      разделитель столбцов.
    :return:                None, если данных для записи нет.
    """
    if not len(infile):
        return None
    try:
        with open(infile, "r"):
            pass
    except FileNotFoundError:
        with open(infile, 'w'):
            pass
    finally:
        with open(infile, "r") as read_file:
            data = json.load(read_file)

    with open(filename, "w", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=delimiter)
        # headers = (['Раздел', 'Артикул', 'Наименование', 'Цена', 'Размер', 'Цвет', 'Фото', 'Описание'])
        # writer.writerow(headers)

        for line in data:
            try:
                line['Раздел']
            except KeyError:
                line['Раздел'] = ''
            try:
                line['Артикул']
            except KeyError:
                line['Артикул'] = ''
            try:
                line['Название']
            except KeyError:
                line['Название'] = ''
            try:
                line['Цена']
            except KeyError:
                line['Цена'] = ''
            try:
                line['Размеры']
            except KeyError:
                line['Размеры'] = ''
            try:
                line['Цвет']
            except KeyError:
                line['Цвет'] = ''
            try:
                line['Картинка']
            except KeyError:
                line['Картинка'] = ''
            try:
                line['Описание']
            except KeyError:
                line['Описание'] = ''

            writer.writerow((line['Раздел'], line['Артикул'], line['Название'], line['Цена'], line['Размеры'],
                             line['Цвет'], line['Картинка'], line['Описание']))


def dirs():
    try:
        os.mkdir('temp')
    except FileExistsError:
        pass
    try:
        os.mkdir(f'temp{PLATFORM_SEP}old_data{PLATFORM_SEP}')
    except FileExistsError:
        pass
    try:
        os.mkdir(f'temp{PLATFORM_SEP}items')
    except FileExistsError:
        pass
    try:
        os.mkdir(f'temp{PLATFORM_SEP}pics')
    except FileExistsError:
        pass

    try:
        os.mkdir(f'temp{PLATFORM_SEP}soup')
    except FileExistsError:
        pass


if __name__ == '__main__':
    dirs()
    main()
