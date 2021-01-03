# this is a server

import socket
import sys
import threading
import pickle

from time import sleep

from cluster import app_init, receive_multicast, send_multicast, leader_election, heartbeat


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (app_init.myIP, app_init.server_port)
buffer_size = 1024
unicode = 'utf-8'

server_exist = False


def clients_handler(connection, address):
    while True:
        try:
            data = connection.recv(buffer_size)
            #check if no data received from a connection or a chat member sent a {quit}
            if not data or data[0] == '{quit}':
                sleep(0.5)

                # if the disconnected address is given in the client_list, a chat member left the chat
                if address[0] in app_init.client_list:
                    print(f'Chat member {address[0]} disconnected')
                    app_init.client_list.remove(address)
                    app_init.client_left = True
                    app_init.network_changed = True

                    for connection in app_init.connections:
                        if connection in app_init.client_list:
                            message = f'{address[0]} left the chat!'
                            connection.send(message.encode(unicode))

                # other connections refer to server heartbeats
                else:
                    print(f'{address[0]} disconnected')

                app_init.connections.remove(connection)
                connection.close()
                break

            else:
                print(f'Message from {address[0]} ==> {data.decode(unicode)}')
                for connection in app_init.connections:
                    if connection in app_init.client_list:
                        message = f'{address[0]} said: {data.decode(unicode)}'
                        connection.send(message.encode(unicode))

        except KeyboardInterrupt:
            print(f'No Connection')


def start_server_binding():

    sock.bind(host_address)
    sock.listen()
    print(f'\n[SERVER] Starting and listening on IP {app_init.myIP} with PORT {app_init.server_port}',
          file=sys.stderr)
    app_init.server_running = True

    while True:
        try:
            connection, address = sock.accept()
            app_init.connections.append(connection)
            print(f'{address[0]} connected')
            print(f'Connection {connection}')
            new_thread(clients_handler, (connection, address))
        except KeyboardInterrupt:
            sock.close()
            print("\nSocket closed")
            break


def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


if __name__ == '__main__':

    multicast_receiver = send_multicast.sending_request_to_multicast(app_init.server_list, app_init.server_leader, app_init.server_leader_crashed, app_init.server_replica_crashed, app_init.client_list)

    if not multicast_receiver:
        app_init.server_list.append(app_init.myIP)
        app_init.server_leader = app_init.myIP

    new_thread(receive_multicast.starting_multicast_receiver, ())

    while True:
        try:
            # if a server replica crashes or the network was changed (client list as well as server list),
            # then the updated lists will be sent to all server who listen on the the multicast group
            if app_init.server_leader == app_init.myIP and app_init.network_changed or app_init.server_replica_crashed:
                sleep(2)
                send_multicast.sending_request_to_multicast(app_init.server_list, app_init.server_leader, app_init.server_leader_crashed, app_init.server_replica_crashed, app_init.client_list)
                app_init.server_replica_crashed = ''

            if app_init.server_leader == app_init.myIP:
                print(f'\n[SERVER] {app_init.myIP} Running ==> {app_init.server_running} '
                      f'\n[SERVER] Server List: {app_init.server_list} ==> Leader: {app_init.server_leader}'
                      f'\n[SERVER] Server Neighbour ==> {app_init.server_neighbour}'
                      f'\n[SERVER] Client List: {app_init.client_list}'
                      f'\n[SERVER] Network Changed ==> {app_init.network_changed}')

            app_init.network_changed = False
            sleep(3)
            new_thread(start_server_binding, ()) if not app_init.server_running else None
            new_thread(heartbeat.start_heartbeat, ()) if not app_init.heartbeat_running and app_init.server_running else None

        except KeyboardInterrupt:
            sock.close()
            print(f'\nClosing Server on IP {app_init.myIP} with PORT {app_init.server_port}', file=sys.stderr)
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
