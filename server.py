try:
    import socket
    import threading
    import os
except:
    print('''[ERROR] Required libraries are not installed! To install them use:
    pip install -r requirements.txt''')

class Server:
    def __init__(self) -> None:
        self.host = None
        self.port = None
        self.users = []
        self.users_amount = 2
        self.thread_msg_list = {}
        
        while True:
            self.host = input("Пожалуйста, введите ip сервера (если не знаете какой, то введите 0): ")
            if self.host == '0':
                self.host = socket.gethostbyname(socket.gethostname())
                break
            if len(self.host) <= 15 and len(self.host) >= 7:
                break
            else:
                print('Данные введены неверно!')

        while True:
            self.port = int(input("Пожалуйста, введите порт (в диапазоне от 1024 до 49151), через который будет работать сервер (если не знаете какой, то введите 0): "))
            if self.port == 0:
                self.port = 9090
            if self.port >= 1024 and self.port <= 49151:
                break
            else:
                print('Данные введены не верно!')
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.users_amount)
        threading.Thread(target=self.__connections_control).start()
        os.system('cls')
        print('[!!!] Сервер запущен')
        if self.host == socket.gethostbyname(socket.gethostname()):
            print(f'IP сервера: {socket.gethostbyname(socket.gethostname())}')
        else:
            print(f'IP сервера: {self.host}')
        print(f'Порт сервера: {self.port}')


    def __connections_control(self) -> None:
        while len(self.users) < self.users_amount:
            conn, addr = self.server.accept()
            if conn not in self.users:
                self.users.append(conn)
                msg_control = threading.Thread(target=self.__message_control, args=[conn])
                msg_control.start()
                self.thread_msg_list[conn] = msg_control

    def __message_control(self, conn) -> None:
        while True:
            try:
                message = conn.recv(1024)

                for client in self.users:
                    client.send(message)
            except socket.error as e:
                self.users.remove(conn)
                del self.thread_msg_list[conn]
                break



server = Server()