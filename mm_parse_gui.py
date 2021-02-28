# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mm_parse_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(440, 250)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(440, 250))
        MainWindow.setMaximumSize(QtCore.QSize(440, 250))
        icon = QtGui.QIcon.fromTheme("icon.ico")
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 440, 220))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(440, 220))
        self.tabWidget.setMaximumSize(QtCore.QSize(440, 220))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_parser = QtWidgets.QWidget()
        self.tab_parser.setObjectName("tab_parser")
        self.parse_button = QtWidgets.QPushButton(self.tab_parser)
        self.parse_button.setGeometry(QtCore.QRect(300, 140, 121, 28))
        self.parse_button.setObjectName("parse_button")
        self.label = QtWidgets.QLabel(self.tab_parser)
        self.label.setGeometry(QtCore.QRect(10, 10, 200, 28))
        self.label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label.setLineWidth(1)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setScaledContents(False)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab_parser)
        self.label_2.setGeometry(QtCore.QRect(10, 40, 200, 28))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tab_parser)
        self.label_3.setGeometry(QtCore.QRect(10, 70, 200, 28))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab_parser)
        self.label_4.setGeometry(QtCore.QRect(10, 100, 200, 28))
        self.label_4.setObjectName("label_4")
        self.username_entry = QtWidgets.QLineEdit(self.tab_parser)
        self.username_entry.setGeometry(QtCore.QRect(220, 10, 200, 28))
        self.username_entry.setObjectName("username_entry")
        self.password_entry = QtWidgets.QLineEdit(self.tab_parser)
        self.password_entry.setGeometry(QtCore.QRect(220, 40, 200, 28))
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_entry.setObjectName("password_entry")
        self.section_combo = QtWidgets.QComboBox(self.tab_parser)
        self.section_combo.setGeometry(QtCore.QRect(220, 70, 200, 28))
        self.section_combo.setObjectName("section_combo")
        self.tabWidget.addTab(self.tab_parser, "")
        self.tab_vk_upload = QtWidgets.QWidget()
        self.tab_vk_upload.setObjectName("tab_vk_upload")
        self.vk_upload_button = QtWidgets.QPushButton(self.tab_vk_upload)
        self.vk_upload_button.setGeometry(QtCore.QRect(300, 140, 121, 41))
        self.vk_upload_button.setObjectName("vk_upload_button")
        self.label_6 = QtWidgets.QLabel(self.tab_vk_upload)
        self.label_6.setGeometry(QtCore.QRect(10, 10, 200, 28))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.tab_vk_upload)
        self.label_7.setGeometry(QtCore.QRect(10, 40, 200, 28))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.tab_vk_upload)
        self.label_8.setGeometry(QtCore.QRect(10, 70, 200, 28))
        self.label_8.setObjectName("label_8")
        self.vk_login_entry = QtWidgets.QLineEdit(self.tab_vk_upload)
        self.vk_login_entry.setGeometry(QtCore.QRect(220, 10, 200, 28))
        self.vk_login_entry.setObjectName("vk_login_entry")
        self.vk_password_entry = QtWidgets.QLineEdit(self.tab_vk_upload)
        self.vk_password_entry.setGeometry(QtCore.QRect(220, 40, 200, 28))
        self.vk_password_entry.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText|QtCore.Qt.ImhSensitiveData)
        self.vk_password_entry.setInputMask("")
        self.vk_password_entry.setText("")
        self.vk_password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.vk_password_entry.setObjectName("vk_password_entry")
        self.group_id_entry = QtWidgets.QLineEdit(self.tab_vk_upload)
        self.group_id_entry.setGeometry(QtCore.QRect(220, 70, 200, 28))
        self.group_id_entry.setObjectName("group_id_entry")
        self.additional_value_entry = QtWidgets.QLineEdit(self.tab_vk_upload)
        self.additional_value_entry.setGeometry(QtCore.QRect(220, 130, 71, 28))
        self.additional_value_entry.setObjectName("additional_value_entry")
        self.label_9 = QtWidgets.QLabel(self.tab_vk_upload)
        self.label_9.setGeometry(QtCore.QRect(10, 130, 200, 28))
        self.label_9.setObjectName("label_9")
        self.label_5 = QtWidgets.QLabel(self.tab_vk_upload)
        self.label_5.setGeometry(QtCore.QRect(10, 100, 200, 28))
        self.label_5.setObjectName("label_5")
        self.section_combo_vk = QtWidgets.QComboBox(self.tab_vk_upload)
        self.section_combo_vk.setGeometry(QtCore.QRect(220, 100, 200, 28))
        self.section_combo_vk.setObjectName("section_combo_vk")
        self.tabWidget.addTab(self.tab_vk_upload, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 440, 25))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.save_as = QtWidgets.QAction(MainWindow)
        self.save_as.setObjectName("save_as")
        self.menu.addAction(self.save_as)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Парсер сайта \"Маленький мир\""))
        self.parse_button.setText(_translate("MainWindow", "Запустить парсинг"))
        self.label.setText(_translate("MainWindow", "Имя пользователя"))
        self.label_2.setText(_translate("MainWindow", "Пароль"))
        self.label_3.setText(_translate("MainWindow", "Раздел"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_parser), _translate("MainWindow", "Парсер"))
        self.vk_upload_button.setText(_translate("MainWindow", "Выгрузить в ВК"))
        self.label_6.setText(_translate("MainWindow", "Логин"))
        self.label_7.setText(_translate("MainWindow", "Пароль"))
        self.label_8.setText(_translate("MainWindow", "ID группы"))
        self.label_9.setText(_translate("MainWindow", "Процент наценки"))
        self.label_5.setText(_translate("MainWindow", "Раздел"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vk_upload), _translate("MainWindow", "Выгрузка в ВК"))
        self.menu.setTitle(_translate("MainWindow", "Сохранить в файл"))
        self.save_as.setText(_translate("MainWindow", "Сохранить как"))
