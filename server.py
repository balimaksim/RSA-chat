import socket
import threading
import os

class Server:
    def __init__(self, users_amount=2) -> None:
        self.host = None
        self.port = None
        self.users = []
        self.users_amount = users_amount
        
        while True:
            os.system('cls')
            self.host = input("Пожалуйста, введите ip сервера (если не знаете какой, то прото нажмие Enter): ")
            if len(self.host) == 0:
                self.host = socket.gethostname()
                break
            if len(self.host) <= 15 and len(self.host) >= 7:
                break
            else:
                print('Данные введены неверно!')

        while True:
            self.port = input("Пожалуйста, введите порт, через который будет работать сервер (если не знаете какой, то прото нажмие Enter): ")
            if len(self.port) == 0:
                self.port = 9090
                break
            if len(self.port) > 0:
                self.port = str(self.port)
            # if len(str(self.port)) <= 5 and len(str(self.port)) >= 4 and type(self.port) == int:
            #     break
            else:
                print('Данные введены не верно!')
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.users_amount)
        threading.Thread(target=self.__connections_control).start()
        os.system('cls')
        print('[!!!] Сервер запущен')
        if self.host == socket.gethostname():
            print(f'IP сервера: {socket.gethostbyname(socket.gethostname())}')
        else:
            print(f'IP сервера: {self.host}')
        print(f'Порт сервера: {self.port}')


    def __connections_control(self) -> None:
        while True:
            conn, addr = self.server.accept()
            print(f'{addr} connected')
            if conn not in self.users:
                self.users.append(conn)
                msg_control = threading.Thread(target=self.__message_control, args=[conn])
                msg_control.start()


    def __message_control(self, conn) -> None:
        while True:
            message = conn.recv(1024)

            print(message)

            for client in self.users:
            #     if conn != client:
                client.send(message)



server = Server(users_amount=2)