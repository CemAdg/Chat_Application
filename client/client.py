import socket
import threading
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '0.0.0.0'
port = 10000
hAddress = (host, port)
bSize = 1024
unicode = 'utf-8'

sock.connect(hAddress)


def sendMsg():
    while True:
        sock.send(input("").encode(unicode))


iThread = threading.Thread(target=sendMsg)
iThread.daemon = True
iThread.start()


while True:
    try:
        data = sock.recv(bSize)
        if not data:
            break
        print(data.decode(unicode))
    except KeyboardInterrupt:
        sock.close()
        print("\nConnection closed")
        break
