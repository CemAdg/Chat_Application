# chat server using multicast

import socket
import struct
import threading
import sys

multicast_addr = '224.0.0.1'
bind_addr = '0.0.0.0'
port = 3000

def receiveMulticastMessage():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    membership = socket.inet_aton(multicast_addr) + socket.inet_aton(bind_addr)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((bind_addr, port))

    while True:
        message, address = sock.recvfrom(255)
        print(message.decode())

def sendMulticastMessage():

    message = input("Enter message to multicast")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    sock.sendto(message.encode(), (multicast_addr, port))
    sock.close()


if __name__ == '__main__':

    first_argv = ""
    listenerStatus = False

    try:
        first_argv = sys.argv[1]

        if first_argv == 'listener' or 'Listener':
            listenerStatus = True
            print('Starting as listener server:')
            thread1 = threading.Thread(target=receiveMulticastMessage)
            thread1.start()
    except:
        pass

    if listenerStatus == False:
        print('Starting as sender server:')
        thread2 = threading.Thread(target=sendMulticastMessage)
        thread2.start()
