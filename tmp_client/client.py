from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread

# GLOBAL CONSTANTS
SERVER = socket(AF_INET, SOCK_DGRAM)  # create a socket to get machine address
SERVER.connect(("8.8.8.8", 80))
HOST = SERVER.getsockname()[0]  # gets the ipv4 address from the machine
PORT = 1000
BUFFER_SIZE = 1024
ADDR = ('localhost', 5000)
FORMAT = "utf8"

# GLOBAL VARIABLES
messages = []

client_socket = socket(AF_INET, SOCK_STREAM)  # create a socket
client_socket.connect(ADDR)  # connect to socket


def receive_messages():
    """
    receive messages from tmp_server
    :return: None
    """
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE).decode()
            messages.append(msg)
            print(msg)
        except Exception as e:
            print("[EXCEPTION]", e)
            break


def send_message(msg):
    """
    send message to tmp_server
    :param msg: str
    :return: None
    """
    client_socket.send(bytes(msg, FORMAT))
    if msg == "{quit}":
        client_socket.close()


receive_thread = Thread(target=receive_messages)
receive_thread.start()

send_message("Tim")
send_message("hello")
