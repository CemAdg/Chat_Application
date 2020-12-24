import socket
import struct
import sys

message ='very important data'
multicast_group = ('224.3.29.71', 10000)
FORMAT = 'utf-8'

# Create the datagram socket
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the timeut so the socket does not block indefinitely when trying to receiver data
SOCKET.settimeout(5)

# Set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
SOCKET.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

try:
    # Send data to the multicast group
    print(f'sending {message}', file=sys.stderr)
    sent = SOCKET.sendto(message.encode('utf-8'), multicast_group)
    print('waiting to receive', file=sys.stderr)

    # Look for responses from all recipients
    while True:
        try:
            data, server = SOCKET.recvfrom(16)
            print(f'received {data.decode(FORMAT)} from {server}', file=sys.stderr)
        except socket.timeout:
            print('waiting to receive', file=sys.stderr)
finally:
    print('closing socket', file=sys.stderr)
    SOCKET.close()