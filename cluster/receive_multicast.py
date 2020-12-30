import socket
import struct
import sys
import pickle
import time

from cluster import hosts, ports


multicast_ip = '224.3.29.71'
server_address = ('', ports.multicast)
buffer_size = 1024
unicode = 'utf-8'

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_data_to_server(address):
    server_exist = False
    server_exist = True if address[0] in hosts.server_list else server_exist

    if server_exist:
        print(f'[MULTICAST RECEIVER {hosts.myIP}] Sending Server List to {address[0]}',
              file=sys.stderr)
        sock.sendto(pickle.dumps([hosts.server_list, hosts.leader]), address)
    else:
        print(f'[MULTICAST RECEIVER {hosts.myIP}] Sending acknowledgement to Multicast Sender {address[0]}',
              file=sys.stderr)
        sock.sendto('acknowledgement'.encode(unicode), address)
        print(f'[MULTICAST RECEIVER {hosts.myIP}] Append {address[0]} to Server List',
              file=sys.stderr)
        hosts.server_list.append(address[0])
        hosts.leader = address[0] if len(hosts.server_list) == 1 else hosts.leader


def starting_multicast():
    try:
        # Bind to the Server address
        sock.bind(server_address)

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(multicast_ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Starting UDP Socket and listening on Port {ports.multicast}',
              file=sys.stderr)

        # Receive/respond loop
        while True:
            try:
                address = sock.recvfrom(buffer_size)[1]
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Request detected from {address[0]}',
                      file=sys.stderr)
                send_data_to_server(address)
            except KeyboardInterrupt:
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                      file=sys.stderr)
                break
    except Exception as e:
        print(f'[MULTICAST RECEIVER {hosts.myIP}] {e}')
