# this is a server

import socket
import sys
import threading
import queue

from time import sleep

from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (hosts.myIP, ports.server)
buffer_size = 1024
unicode = 'utf-8'
FIFO = queue.Queue()


def printer():
    sleep(0.5)
    print(f'\n[SERVER] Server List: {hosts.server_list} ==> Leader: {hosts.leader}'
          f'\n[SERVER] Client List: {hosts.client_list}'
          f'\n[SERVER] Clients: {len(hosts.client_list)}'
          f'\n[SERVER] Neighbour ==> {hosts.neighbour}\n')


def update_clients():
    message = ''
    while not FIFO.empty():
        message += f'{FIFO.get()}'
        message += '\n' if not FIFO.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(unicode))


def client_handler(client, address):
    while True:
        try:
            data = client.recv(buffer_size)
            if not data:
                sleep(0.5)
                print(f'{address[0]} disconnected')
                FIFO.put(f'\n{address[0]} disconnected\n')
                hosts.client_list.remove(client)
                client.close()
                printer()
                break
            FIFO.put(f'{address[0]} said: {data.decode(unicode)}')
            print(f'Message from {address[0]} ==> {data.decode(unicode)}')
        except Exception as e:
            print(e)
            break


def start_binding():
    sock.bind(host_address)
    sock.listen()
    print(f'\n[SERVER] Starting and listening on IP {hosts.myIP} with PORT {ports.server}',
          file=sys.stderr)

    while True:
        try:
            client, address = sock.accept()
            if address[0] not in hosts.server_list or address[0] == hosts.myIP:
                print(f'{address[0]} connected')
                FIFO.put(f'\n{address[0]} connected\n')
                print(client)
                hosts.client_list.append(client)

                new_thread(client_handler, (client, address))
                printer()
        except Exception as e:
            print(e)
            break


def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    printer()

    multicast_receiver = send_multicast.sending_request_to_multicast()

    if not multicast_receiver:
        hosts.server_list.append(hosts.myIP)
        hosts.leader = hosts.myIP
    new_thread(receive_multicast.starting_multicast_receiver, ())
    new_thread(start_binding, ())
    new_thread(heartbeat.start_heartbeat, ())

    while True:
        try:
            if hosts.leader == hosts.myIP and hosts.network_changed or hosts.replica_crashed:
                if hosts.leader_crashed:
                    hosts.client_list = []
                send_multicast.sending_request_to_multicast()
                hosts.leader_crashed = False
                hosts.replica_crashed = ''
                hosts.network_changed = False
                printer()

            if hosts.leader != hosts.myIP and hosts.network_changed:
                hosts.network_changed = False
            update_clients()
        except KeyboardInterrupt:
            sock.close()
            print(f'\nClosing Server on IP {hosts.myIP} with PORT {ports.server}', file=sys.stderr)
            break
