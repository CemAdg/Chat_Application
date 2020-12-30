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

isLeader = bool(input())
server_exist = False

if __name__ == '__main__':
    while True:
        try:
            for server in hosts.server_list:
                server_exist = True if server[0] == host_address[0] else server_exist

            if not server_exist:
                multicast_sender = send_multicast.sending_request_to_multicast()
                if isLeader and not multicast_sender:
                    t1 = threading.Thread(target=receive_multicast.starting_multicast, args=())
                    t1.daemon = True
                    t1.start()
            time.sleep(1)
            print('loop done')
            time.sleep(3)




            """for server in hosts.server_list:
                server_exist = True if server[0] == host_address[0] else server_exist

            if server_exist:
                send_multicast.update_server_list()
            else:
                time.sleep(1)
                multicast_sender = send_multicast.sending_request_to_multicast()
                if not multicast_sender:
                    t1 = threading.Thread(target=receive_multicast.starting_multicast, args=())
                    t1.daemon = True
                    t1.start()
            time.sleep(1)
            print(hosts.server_list)
            time.sleep(5)"""


            """t2 = threading.Thread(target=send_multicast.update_server_list(), args=())
            t2.daemon = True
            t2.start()
            time.sleep(1)
            receive_multicast.send_server_list()
            time.sleep(2)
            #print(send_multicast.update_server_list())
            #print(hosts.server_list)
            time.sleep(10)"""



            """sock.bind(host_address)
            sock.listen()
            print(f'Starting Server and listening on IP {host} with PORT {port}', file=sys.stderr)
            sock.accept()"""
        except KeyboardInterrupt:
            print(f'\nClosing Server on IP {host} with PORT {port}', file=sys.stderr)
            sock.close()
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