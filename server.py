# this is main server

import socket
import threading
import sys
import time
from cluster import ports, receive_multicast, send_multicast


# sys.path.append(os.path.dirname(os.path.abspath("")))

# import cluster.receive_multicast
# from cluster import leader_election

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = ports.server
host_address = (host, port)
buffer_size = 1024
unicode = 'utf-8'

connections = []
server_list = []
leader_server = ''
for thread in threading.enumerate():
    print(thread.name)

if __name__ == "__main__":
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
