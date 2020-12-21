from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


def wait_for_connection():
   run = True
   while run:
       client, addr = SERVER.accept()


SERVER = socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER.connect(("8.8.8.8", 80))

HOST = SERVER.getsockname()[0]
PORT = 5500
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=wait_for_connection, ())
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()