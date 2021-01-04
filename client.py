import socket
import threading

from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
leader_address = ('19.10.19.20', ports.server)
buffer_size = 1024
unicode = 'utf-8'


def send_message():
    while True:
        try:
            sock.send(input("").encode(unicode))
        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break


def receive_message():
    hosts.client_running = True
    while True:
        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))
        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break


def new_thread(target, args, join):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()
    t.join() if join else None


if __name__ == '__main__':
    sock.connect(leader_address)
    while True:
        new_thread(send_message, (), False) if not hosts.client_running else None
        new_thread(receive_message, (), False) if not hosts.client_running else None
    """while True:
        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))
        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break"""
