from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, getfqdn
from threading import Thread

SERVER = socket(AF_INET, SOCK_DGRAM)  # create a socket to get machine address
SERVER.connect(("8.8.8.8", 80))
HOST = SERVER.getsockname()[0]  # gets the ipv4 address from the machine
PORT = 10000
BUFFER_SIZE = 1024
HOST_ADDRESS = (HOST, PORT)
FORMAT = "utf-8"

CLIENT = socket(AF_INET, SOCK_STREAM)
CLIENT.connect(HOST_ADDRESS)

alias = input('Choose an alias >>> ')


def client_receive():
    while True:
        try:
            message = CLIENT.recv(BUFFER_SIZE).decode(FORMAT)
            if message == "alias?":
                CLIENT.send(alias.encode(FORMAT))
            else:
                print(message)
        except:
            print('Error!')
            break


def client_send():
    while True:
        try:
            message = input('')
            if message == 'exit':
                CLIENT.close()
            else:
                CLIENT.send(message.encode(FORMAT))
                print(f'\nMe: {message}')
        except:
            print('EXCEPTION')
            CLIENT.close()
            break


receive_thread = Thread(target=client_receive)
receive_thread.start()

send_thread = Thread(target=client_send)
send_thread.start()
