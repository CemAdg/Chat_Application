import socket
import struct
import sys
import pickle

from time import sleep

from cluster import hosts, ports

multicast_address = (hosts.multicast, ports.multicast)
multicast_address_client = (hosts.multicast, ports.multicast_client)
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
    print(f'\n[MULTICAST SENDER {hosts.myIP}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps([server_list, leader, leader_crashed, replica_crashed])
    sock.sendto(message, multicast_address)
    try:
        data, address = sock.recvfrom(buffer_size)
        if hosts.leader == hosts.myIP:
            print(f'[MULTICAST SENDER {hosts.myIP}] All Servers have been updated',
                  file=sys.stderr)
        return True
    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.myIP}] Multicast Receiver not detected',
              file=sys.stderr)
        return False


def send_join_chat_message_to_multicast(name):
    # Send data to the Multicast address
    print(f'\n[MULTICAST SENDER] {hosts.myIP} sending join chat request to Multicast Address {multicast_address_client}',
          file=sys.stderr)
    message = pickle.dumps(['JOIN', name])
    sock.sendto(message, multicast_address)
    sleep(3)
    try:
        data, address = sock.recvfrom(buffer_size)
        hosts.client_list = pickle.loads(data)[0]
        hosts.server_leader = pickle.loads(data)[1]
    except Exception as e:
        print(e)
        print(f'[MULTICAST SENDER {hosts.myIP}] Multicast Receiver not detected -> chat server offline',
              file=sys.stderr)