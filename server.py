# this is a Server

# import Modules
import socket
import sys
import threading
import queue

from cluster import hosts, ports, receive_multicast, send_multicast, heartbeat

# creating TCP Socket for Server
# get the own IP from cluster.hosts
# get the port used for Server from cluster.ports
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (hosts.myIP, ports.server)

# create First In First Out Queue
FIFO = queue.Queue()

# terminal printer for info
def printer():
    print(f'\n[SERVER] Server List: {hosts.server_list} ==> Leader: {hosts.leader}'
          f'\n[SERVER] Client List: {hosts.client_list}'
          f'\n[SERVER] Neighbour ==> {hosts.neighbour}\n')


# standardized for creating and starting Threads
def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


# send all messages from FIFO Queue to all Clients
def send_clients():
    message = ''
    while not FIFO.empty():
        message += f'{FIFO.get()}'
        message += '\n' if not FIFO.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(hosts.unicode))


# handle all received messages from connected Clients
def client_handler(client, address):
    while True:
        try:
            data = client.recv(hosts.buffer_size)

            # if Client is disconnected or lost the connection
            if not data:
                print(f'{address} disconnected')
                FIFO.put(f'\n{address} disconnected\n')
                hosts.client_list.remove(client)
                client.close()
                break

            FIFO.put(f'{address} said: {data.decode(hosts.unicode)}')
            print(f'Message from {address} ==> {data.decode(hosts.unicode)}')

        except Exception as e:
            print(e)
            break


# bind the TCP Server Socket and listen for connections
def start_binding():
    sock.bind(host_address)
    sock.listen()
    print(f'\n[SERVER] Starting and listening on IP {hosts.myIP} with PORT {ports.server}',
          file=sys.stderr)

    while True:
        try:
            client, address = sock.accept()
            data = client.recv(hosts.buffer_size)

            # used just for Chat-Clients (filter out heartbeat)
            if data:
                print(f'{address} connected')
                FIFO.put(f'\n{address} connected\n')
                hosts.client_list.append(client)
                new_thread(client_handler, (client, address))

        except Exception as e:
            print(e)
            break


# main Thread
if __name__ == '__main__':

    # trigger Multicast Sender to check if a Multicast Receiver with given Multicast Address from cluster.hosts exists
    multicast_receiver_exist = send_multicast.sending_request_to_multicast()

    # append the own IP to the Server List and assign the own IP as the Server Leader
    if not multicast_receiver_exist:
        hosts.server_list.append(hosts.myIP)
        hosts.leader = hosts.myIP

    # calling functions as Threads
    new_thread(receive_multicast.starting_multicast_receiver, ())
    new_thread(start_binding, ())
    new_thread(heartbeat.start_heartbeat, ())

    # loop main Thread
    while True:
        try:
            # send Multicast Message to all Multicast Receivers (Servers)
            # used from Server Leader or if a Server Replica recognizes another Server Replica crash
            if hosts.leader == hosts.myIP and hosts.network_changed or hosts.replica_crashed:
                if hosts.leader_crashed:
                    hosts.client_list = []
                send_multicast.sending_request_to_multicast()
                hosts.leader_crashed = False
                hosts.network_changed = False
                hosts.replica_crashed = ''
                printer()

            # used from Server Replica to set the variable to False
            if hosts.leader != hosts.myIP and hosts.network_changed:
                hosts.network_changed = False
                printer()

            # function to send the FIFO Queue messages
            send_clients()

        except KeyboardInterrupt:
            sock.close()
            print(f'\nClosing Server on IP {hosts.myIP} with PORT {ports.server}', file=sys.stderr)
            break
