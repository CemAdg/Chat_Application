# this is a server

import socket
import sys
import threading

from time import sleep

from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (hosts.myIP, ports.server)
buffer_size = 1024
unicode = 'utf-8'

server_exist = False


def printer():
    sleep(0.5)
    print(f'\n[SERVER] Running ==> {hosts.server_running}'
          f'\n[SERVER] Server List: {hosts.server_list} ==> Leader: {hosts.leader}'
          f'\n[SERVER] Client List: {hosts.client_list}'
          f'\n[SERVER] Neighbour ==> {hosts.neighbour}'
          f'\n[SERVER] Network Changed ==> {hosts.network_changed}\n')


def client_handler(client, address):
    while True:
        try:
            data = client.recv(buffer_size)
            if not data:
                sleep(0.5)
                print(f'{address[0]} disconnected')
                hosts.client_list.remove(client)
                #hosts.client_list.remove(client.getpeername())
                client.close()

                # send updated list to all replica
                #new_thread(send_multicast.sending_request_to_multicast, (), True)

                new_thread(printer, (), True)
                break
            for client in hosts.client_list:
                client.send(f'{address[0]} said: {data.decode(unicode)}'.encode(unicode))
            print(f'Message from {address[0]} ==> {data.decode(unicode)}')
        except KeyboardInterrupt:
            print(f'No Connection')
            break


def start_binding():
    hosts.server_running = True
    sock.bind(host_address)
    sock.listen()
    print(f'\n[SERVER] Starting and listening on IP {hosts.myIP} with PORT {ports.server}',
          file=sys.stderr)

    while True:
        try:
            client, address = sock.accept()
            if address[0] not in hosts.server_list:
                print(f'{address[0]} connected')
                print(client)
                hosts.client_list.append(client)

                #hosts.client_list.append(client.getpeername())

                # send updated list to all replica
                #new_thread(send_multicast.sending_request_to_multicast, (), True)

                # start communication between chat clients
                new_thread(client_handler, (client, address), False)
                new_thread(printer, (), True)
        except KeyboardInterrupt:
            sock.close()
            print("\nSocket closed")
            break


def new_thread(target, args, join):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()
    t.join() if join else None


if __name__ == '__main__':
    printer()

    multicast_receiver = send_multicast.sending_request_to_multicast()

    if not multicast_receiver:
        hosts.server_list.append(hosts.myIP)
        hosts.leader = hosts.myIP
    new_thread(receive_multicast.starting_multicast_receiver, (), False)

    while True:
        try:
            if hosts.leader == hosts.myIP and hosts.network_changed or hosts.replica_crashed:
                if hosts.leader_crashed == True:
                    hosts.client_list = []
                new_thread(send_multicast.sending_request_to_multicast, (), True)
                hosts.leader_crashed = False
                hosts.replica_crashed = ''
                hosts.network_changed = False
                new_thread(printer, (), True)

            if hosts.leader != hosts.myIP and hosts.network_changed:
                hosts.network_changed = False

            new_thread(start_binding, (), False) if not hosts.server_running else None
            new_thread(heartbeat.start_heartbeat, (), False) if not hosts.heartbeat_running and hosts.server_running else None
        except KeyboardInterrupt:
            sock.close()
            print(f'\nClosing Server on IP {hosts.myIP} with PORT {ports.server}', file=sys.stderr)
            break
