# this is a server

import socket
import sys
import threading

from time import sleep

from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_address = (hosts.myIP, ports.server)
buffer_size = 1024
unicode = 'utf-8'

server_exist = False
server_running = False


def client_handler(connection, address):
    while True:
        try:
            data = connection.recv(buffer_size)
            if not data:
                print(f'{address[0]} disconnected\n')
                hosts.connections.remove(connection)
                connection.close()
                break
            for connection in hosts.connections:
                connection.send(f'{address[0]} said: {data.decode(unicode)}'.encode(unicode))
            print(f'Message from {address[0]} ==> {data.decode(unicode)}')
        except KeyboardInterrupt:
            print(f'No Connection')


def start_binding():
    global server_running
    sock.bind(host_address)
    sock.listen()
    print(f'\n[SERVER] Starting and listening on IP {hosts.myIP} with PORT {ports.server}',
          file=sys.stderr)
    server_running = True

    while True:
        try:
            connection, address = sock.accept()
            hosts.connections.append(connection)
            print(f'{address[0]} connected')
            new_thread(client_handler, (connection, address))
        except KeyboardInterrupt:
            sock.close()
            print("\nSocket closed")
            break


def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


if __name__ == '__main__':

    multicast_receiver = send_multicast.sending_request_to_multicast(hosts.server_list, hosts.leader, hosts.leader_crashed, hosts.non_leader_crashed)

    if not multicast_receiver:
        hosts.server_list.append(hosts.myIP)
        hosts.leader = hosts.myIP

    new_thread(receive_multicast.starting_multicast_receiver, ())
    new_thread(heartbeat.start_heartbeat, ())

    while True:
        try:
            if hosts.leader == hosts.myIP and hosts.network_changed:
                sleep(2)
                send_multicast.sending_request_to_multicast(hosts.server_list, hosts.leader, hosts.leader_crashed, hosts.non_leader_crashed)

            if hosts.network_changed:
                print(f'\n[SERVER] Running ==> {server_running}')
                print(f'[SERVER] List: {hosts.server_list} ==> Leader: {hosts.leader}')
                print(f'[SERVER] Neighbour ==> {hosts.neighbour}')
                print(f'[SERVER] Network Changed ==> {hosts.network_changed}')

            hosts.network_changed = False

            sleep(2)
            new_thread(start_binding, ()) if not server_running else None
        except KeyboardInterrupt:
            print(f'\nClosing Server on IP {hosts.myIP} with PORT {ports.server}', file=sys.stderr)
            break









    """while True:
        try:
            server_exist = True if hosts.myIP in hosts.server_list else server_exist

            if not server_exist or hosts.leader_crashed or hosts.non_leader_crashed:
                multicast_sender = send_multicast.sending_request_to_multicast(hosts.non_leader_crashed)
                new_thread(receive_multicast.starting_multicast, ()) if not multicast_sender else None
                hosts.non_leader_crashed = False

            time.sleep(0.5)

            neighbour_server = leader_election.start_leader_election(hosts.server_list, hosts.myIP)

            print(f'\n[This Server_running] ==> {server_running}')
            print(f'[Server List] {hosts.server_list} ==> Leader: {hosts.leader}')
            print(f'[Neighbour] ==> {neighbour_server}')

            time.sleep(0.5)

            new_thread(start_binding, ()) if not server_running else None

            time.sleep(3)

            print(f'[Heartbeat] {heartbeat.start_heartbeat()}', file=sys.stderr) if neighbour_server else None

            # new_thread(heartbeat.start_heartbeat, ()) if neighbour_server else None

        except KeyboardInterrupt:
            print(f'\nClosing Server on IP {hosts.myIP} with PORT {ports.server}', file=sys.stderr)
            break"""
