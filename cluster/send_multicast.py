import socket
import struct
import sys
import pickle
import server
from time import sleep
from cluster import hosts, ports

multicast_address = (hosts.multicast, ports.multicast)
buffer_size = 1024
unicode = 'utf-8'

# Create the datagram socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the timeout so the socket does not block indefinitely when trying to receiver data
sock.settimeout(0.5)

# Set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


def sending_request_to_multicast():
    sleep(1)

    # Send data to the Multicast address - server communication
    print(f'\n[MULTICAST SENDER {hosts.myIP}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps([hosts.server_list, hosts.leader, hosts.leader_crashed, hosts.replica_crashed, str(hosts.client_list)])
    sock.sendto(message, multicast_address)
    try:
        data, address = sock.recvfrom(buffer_size)
        server.new_thread(server.printer, (), True)
        if hosts.leader == hosts.myIP:
            print(f'[MULTICAST SENDER {hosts.myIP}] All Servers have been updated',
                  file=sys.stderr)
        return True
    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.myIP}] Multicast Receiver not detected',
              file=sys.stderr)
        return False

def sending_join_chat_request_to_multicast():

    # function started from client
    print(f'\n[MULTICAST SENDER {hosts.myIP}] Sending join chat request to Multicast Address {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicast_address)
    try:
        data, address = sock.recvfrom(buffer_size)
        hosts.leader = pickle.loads(data)[0]

    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.myIP}] Multicast Receiver not detected -> Chat Server offline',
              file=sys.stderr)