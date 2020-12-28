import socket
import struct
import sys

from cluster import ports


message = 'I am a new Server'
mutlicast_group = ('224.3.29.71', ports.multicast)
buffer_size = 16
unicode = 'utf-8'

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the timeut so the socket does not block indefinitely when trying to receiver data
sock.settimeout(1)

# Set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

def sending_request_to_multicast():
    try:
        # Send data to the multicast group
        sent = sock.sendto(message.encode('utf-8'), mutlicast_group)
        print(f'sending data to {mutlicast_group}', file=sys.stderr)

        # Look for responses from all recipients
        while True:
            try:
                data, server = sock.recvfrom(buffer_size)
                print(f'Multicast response with --{data.decode(unicode)}-- from {server}', file=sys.stderr)
                #return True
            except socket.timeout:
                print('timed out, no more responses', file=sys.stderr)
                break
    finally:
        print('closing UDP socket from Multicast sender', file=sys.stderr)
        sock.close()