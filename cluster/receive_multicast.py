import socket
import struct
import sys
import pickle

from cluster import hosts, ports


multicast_ip = '224.3.29.71'
server_address = ('', ports.multicast)
buffer_size = 1024
unicode = 'utf-8'

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def starting_multicast_receiver():
    # Bind to the Server address
    sock.bind(server_address)
    # Tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Starting UDP Socket and listening on Port {ports.multicast}',
          file=sys.stderr)

    # Receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(buffer_size)

            print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Received data from {address[0]}',
                  file=sys.stderr)

            if len(pickle.loads(data)[0]) == 0:
                hosts.server_list.append(address[0]) if address[0] not in hosts.server_list else hosts.server_list
            elif pickle.loads(data)[1] and hosts.leader != hosts.myIP:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                hosts.leader_crashed = pickle.loads(data)[2]
                hosts.non_leader_crashed = pickle.loads(data)[3]
                print(f'[MULTICAST RECEIVER {hosts.myIP}] All Data have been updated',
                      file=sys.stderr)

            sock.sendto('ack'.encode(unicode), address)
            hosts.network_changed = True
        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                  file=sys.stderr)
            break
