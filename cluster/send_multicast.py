import socket
import struct
import sys
import pickle
from time import sleep

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


def sending_request_to_multicast(server_list, leader, leader_crashed, replica_crashed, client_list):

    # Send data to the Multicast address
    print(f'\n[MULTICAST SENDER {app_init.myIP}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps([server_list, leader, leader_crashed, replica_crashed, client_list])
    sock.sendto(message, multicast_address)
    try:
        data, address = sock.recvfrom(buffer_size)
        if app_init.server_leader == app_init.myIP:
            print(f'[MULTICAST SENDER {app_init.myIP}] All Servers have been updated',
                  file=sys.stderr)
        return True
    except Exception as e:
        print(e)
        print(f'[MULTICAST SENDER {app_init.myIP}] Multicast Receiver not detected',
              file=sys.stderr)
        return False


def send_join_chat_message_to_multicast(client_membername):
    # Send data to the Multicast address
    print(f'\n[MULTICAST SENDER] {app_init.myIP} sending join chat request to Multicast Address {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps(['JOIN', client_membername])
    sock.sendto(message, multicast_address)
    sleep(3)
    try:
        data, address = sock.recvfrom(buffer_size)
        app_init.client_list = pickle.loads(data)[0]
        app_init.server_leader = pickle.loads(data)[1]
    except Exception as e:
        print(e)
        print(f'[MULTICAST SENDER {app_init.myIP}] Multicast Receiver not detected -> chat server offline',
              file=sys.stderr)
