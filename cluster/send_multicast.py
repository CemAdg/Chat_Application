import socket
import struct
import sys
import pickle

from cluster import app_init

multicast_address = (app_init.multicast_ipaddress, app_init.multicast_port)
buffer_size = 1024
unicode = 'utf-8'

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the timeout so the socket does not block indefinitely when trying to receiver data
sock.settimeout(1)

# Set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


def sending_request_to_multicast(server_list, leader, leader_crashed, replica_crashed):

    # Send data to the Multicast address
    print(f'\n[MULTICAST SENDER {app_init.myIP}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps([server_list, leader, leader_crashed, replica_crashed])
    sock.sendto(message, multicast_address)
    try:
        data, address = sock.recvfrom(buffer_size)
        if app_init.server_leader == app_init.myIP:
            print(f'[MULTICAST SENDER {app_init.myIP}] All Servers have been updated',
                  file=sys.stderr)
        return True
    except socket.timeout:
        print(f'[MULTICAST SENDER {app_init.myIP}] Multicast Receiver not detected',
              file=sys.stderr)
        return False
