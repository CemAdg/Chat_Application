import socket
import struct
import sys

multicast_group = '224.3.29.71'
server_address = ('', 10000)
FORMAT = 'utf-8'

# Create the socket
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
SOCKET.bind(server_address)


# Tell the operating system to add the socket to the multicast group
# on all interfaces.
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
SOCKET.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    try:
        print('\nwaiting to receive message', file=sys.stderr)
        data, address = SOCKET.recvfrom(1024)

        print(f'received {len(data)} bytes from {address}', file=sys.stderr)
        print(data.decode(FORMAT), file=sys.stderr)

        print(f'sending acknowledgement to {address}', file=sys.stderr)
        SOCKET.sendto(('ack').encode(FORMAT), address)
    except:
        print('ack already sent')