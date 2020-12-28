import socket
import struct
import sys
import time

from cluster import ports


multicast_group = '224.3.29.71'
server_address = ('', ports.multicast)
buffer_size = 1024
unicode = 'utf-8'


# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_list = []


def starting_multicast():
    try:
        # Bind to the server address
        sock.bind(server_address)

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Receive/respond loop
        while True:
            try:
                print(f'\nMulticast Listening on Port {ports.multicast}', file=sys.stderr)
                data, address = sock.recvfrom(buffer_size)
                server_list.append(address)
                print(f'Request detected from {address}', file=sys.stderr)

                print(f'sending acknowledgement to {address}', file=sys.stderr)
                sock.sendto('acknowledgement'.encode(unicode), address)
            except KeyboardInterrupt:
                print('closing UDP socket from Multicast receiver', file=sys.stderr)
                break
    except Exception as e:
        print(e)
