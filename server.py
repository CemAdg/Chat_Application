# this is a server

import socket
import sys
import threading
import time

from cluster import hosts, ports, receive_multicast, send_multicast


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = hosts.myIP
port = ports.server
host_address = (host, port)
buffer_size = 1024
unicode = 'utf-8'

is_leader = bool(input())
leader_crashed = False
server_exist = False


def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


def client_handler(connection, address):
    while True:
        try:
            data = connection.recv(buffer_size)
            if not data:
                print(f'{address[0]} disconnected')
                hosts.connections.remove(connection)
                connection.close()
                break
            for connection in hosts.connections:
                connection.send(f'{address[0]} said: {data.decode(unicode)}'.encode(unicode))
            print(f'Messsage from {address[0]} ==> {data.decode(unicode)}')
        except KeyboardInterrupt:
            print(f'No Connection')


def start_binding():
    sock.bind(host_address)
    sock.listen()
    print(f'Starting Server and listening on IP {host} with PORT {port}', file=sys.stderr)

    while True:
        try:
            connection, address = sock.accept()
            new_thread(client_handler, (connection, address))
            hosts.connections.append(connection)
            print(f'{address[0]} connected')
        except KeyboardInterrupt:
            sock.close()
            print("\nSocket closed")
            break


if __name__ == '__main__':
    while True:
        try:
            server_exist = True if host in hosts.server_list else server_exist

            if not server_exist or leader_crashed:
                multicast_sender = send_multicast.sending_request_to_multicast()
                new_thread(receive_multicast.starting_multicast, ()) if is_leader and not multicast_sender else None
                #new_thread(start_binding, ()) if is_leader and multicast_sender else None
            time.sleep(1)
            print(hosts.server_list)
            time.sleep(3)

            #leader_crashed = bool(input()) if server_exist else leader_crashed

            #is_leader = True if leader_crashed else is_leader


            """sock.bind(host_address)
            sock.listen()
            print(f'Starting Server and listening on IP {host} with PORT {port}', file=sys.stderr)
            sock.accept()"""
        except KeyboardInterrupt:
            print(f'\nClosing Server on IP {host} with PORT {port}', file=sys.stderr)
            break












"""if __name__ == "__main__":
    t1 = threading.Thread(target=receive_multicast.starting_multicast, args=())
    t1.start()
    time.sleep(1)
    for thread in threading.enumerate():
        print(thread.name)

    time.sleep(1)
    if send_multicast.sending_request_to_multicast():
        server_list = receive_multicast.server_list
    for thread in threading.enumerate():
        print(thread.name)
    time.sleep(1)
    print()
    #print(f'Leader Server {leader_server}')
    print(f'Server List {server_list}')

    sock.bind(host_address)
    sock.listen(1)
    print(f'Server is running and listening on IP {host} with PORT {port}', file=sys.stderr)
    
    for thread in threading.enumerate():
    print(thread.name)
    
    # leader_election.start_leader_election(server_list, leader)

    while True:
        try:
            c, a = sock.accept()
            cThread = threading.Thread(target=handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            print(f'{a[0]}:{a[1]} connected')
            time.sleep(0.05)
            print('RUNNING THREADS', file=sys.stderr)
            time.sleep(0.05)
            for thread in threading.enumerate():
                print(thread.name)
            time.sleep(0.05)
            print('---------------', file=sys.stderr)
        except KeyboardInterrupt:
            sock.close()
            print("\nConnection closed")
            break
"""