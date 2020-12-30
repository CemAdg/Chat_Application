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

server_list = []

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_server_list():
    global server_list
    for server in server_list:
        print(f'[MULTICAST RECEIVER {hosts.myIP}] Sending Server List to Multicast Sender {server}',
              file=sys.stderr)
        sock.sendto(pickle.dumps(server_list), server)


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
                data, address = sock.recvfrom(buffer_size)
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Request detected from {address}',
                      file=sys.stderr)
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Sending acknowledgement to Multicast Sender {address}',
                      file=sys.stderr)
                sock.sendto('acknowledgement'.encode(unicode), address)
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Adding {address} to Server List',
                      file=sys.stderr)
                hosts.server_list.append(address)
            except KeyboardInterrupt:
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                      file=sys.stderr)
                break
    except Exception as e:
        print(f'[MULTICAST RECEIVER {hosts.myIP}] {e}')
