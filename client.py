from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from design import *
import threading
import shelve
import socket
import rsa
import sys
import os


# class MessageContorller(QThread):
#     def __init__(self, window, socket):
#         super().__init__()
#         self.window = window
#         self.socket = socket

#     def run(self):
#         while True:
#             data = self.socket.recv(1024)

#             self.window.msg_plainTextEdit.setFocus()
#             with shelve.open('private\private') as file:
#                 msg = rsa.decrypt(data, file['private_key'])

#                 self.window.msg_plainTextEdit.appendPlainText(f'[Вы]:\t{msg.decode("utf-8")}')


class Client(QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_RSAchat()
        self.ui.setupUi(self)

        self.ip = None
        self.port = None
        self.public_key = None
        self.private_key = None
        self.friend_key = None
        self.from_me = False

        if os.path.exists('public\public.dat') and os.path.exists('private\private.dat'):
            with shelve.open('public\public') as file:
                self.ip = file['ip']
                self.port = file['port']
                self.public_key = file['public_key']
            with shelve.open('private\private') as file:
                self.private_key = file['private_key']

        self.ui.conn_btn.clicked.connect(self.__connect)
        self.ui.generate_btn.clicked.connect(self.__generate_file)
        self.ui.send_btn.clicked.connect(self.__send_message)
        self.ui.disc_btn_yes_2.clicked.connect(self.__disconnect)


    def __connect(self):
        try:
            self.sock = socket.socket()
            self.msg_get_thread = threading.Thread(target=self.__get_messages)
            # self.MessageControllerThread = MessageContorller(window=self.ui, socket=self.sock)

            if not os.path.exists('private\private.dat'):
                self.ui.result_plainTextEdit.clear()
                self.ui.result_plainTextEdit.appendPlainText('Для начала нужно сгенерировать и обменяться public файлами с собеседником (см. Инструкцию).')
            if not os.path.exists('public\public.dat'):
                self.ui.result_plainTextEdit.clear()
                self.ui.result_plainTextEdit.appendPlainText('Не найден private файл. Попробуйе повторно сгенерировать файлы.')
            else:
                with shelve.open('public\public') as file:
                    self.sock.connect((file['ip'], int(file['port'])))
                self.msg_get_thread.start()

                self.ui.status_connect.raise_()
                self.ui.send_btn.setEnabled(True)

                self.ui.result_plainTextEdit.clear()
                self.ui.result_plainTextEdit.appendPlainText('Вы успешно подключились!')
                self.ui.disconnect_btn.show()

                self.ui.msg_plainTextEdit.clear()
                self.ui.msg_plainTextEdit.appendPlainText('\t\t Вы подключились!')

                self.__send_message('\n\t\t---user_connect---\n', True)
        except Exception as e:
            print(e)
            self.ui.result_plainTextEdit.clear()
            self.ui.result_plainTextEdit.appendPlainText('Неверно введены данные!')


    def __generate_file(self):
        if len(str(self.ui.ip_input_2.text())) > 0 and len(str(self.ui.ip_input_2.text())) <= 15 and len(str(self.ui.ip_input_2.text())) >= 7:
            if len(str(self.ui.port_input_2.text())) > 0 and len(str(self.ui.port_input_2.text())) <= 5 and len(str(self.ui.port_input_2.text())) >= 4:
                (public_key, private_key) = rsa.newkeys(512)
                with shelve.open('public\public') as file:
                    file['public_key'] = public_key
                    file['ip'] = str(self.ui.ip_input_2.text())
                    file['port'] = int(self.ui.port_input_2.text())
                
                with shelve.open('private\private') as file:
                    file['public_key'] = public_key
                    file['private_key'] = private_key

                self.ui.result_plainTextEdit_2.clear()
                self.ui.result_plainTextEdit_2.appendPlainText('Файлы созданы успешно!')
                self.ui.result_plainTextEdit_2.appendPlainText('Папку "public" передайте своему собесенику')
            else:
                self.ui.result_plainTextEdit_2.clear()
                self.ui.result_plainTextEdit_2.appendPlainText('Порт введён неверно!')
        else:
            self.ui.result_plainTextEdit_2.clear()
            self.ui.result_plainTextEdit_2.appendPlainText('IP введён неверно!')


    def __send_message(self, message=None, notification=False):
        print(message)
        if len(str(self.ui.send_input.text())) > 0:
            msg = str(self.ui.send_input.text())
            with shelve.open('public\public') as file:
                self.sock.send(rsa.encrypt(msg.encode('utf-8'), file['public_key']))
                self.from_me = True if not notification else False
            msg = None
            self.ui.send_input.clear()
        if message:
            msg = message
            with shelve.open('public\public') as file:
                self.sock.send(rsa.encrypt(msg.encode('utf-8'), file['public_key']))
                self.from_me = True if not notification else False
            msg = None
    
        
    def __get_messages(self):
        while True:
            try:
                data = self.sock.recv(2048)

                self.ui.msg_plainTextEdit.setFocus()
                with shelve.open('private\private') as file:
                    msg = rsa.decrypt(data, file['private_key'])

                    if self.from_me:
                        self.ui.msg_plainTextEdit.appendPlainText(f'[Вы]:\t{msg.decode("utf-8")}')
                        self.from_me = False
                    else:
                        self.ui.msg_plainTextEdit.appendPlainText(msg.decode('utf-8'))
            except socket.error as e:
                print(e)
                break
            


    def __disconnect(self):
        self.__send_message('\t\t---user_disconnect---', True)
        self.sock.close()
        self.ui.disconnect_btn.hide()
        self.ui.frame_disconnect.lower()
        self.ui.msg_plainTextEdit.clear()
        self.ui.status_connect.lower()
        self.ui.ip_input.clear()
        self.ui.port_input.clear()
        self.ui.result_plainTextEdit.clear()
        self.ui.ip_input_2.clear()
        self.ui.port_input_2.clear()
        self.ui.result_plainTextEdit_2.clear()


def application():
    app = QApplication(sys.argv)
    client = Client()

    client.show()
    sys.exit(app.exec_())


application()