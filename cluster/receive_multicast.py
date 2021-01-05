import socket
import struct
import sys
import pickle
import server

from cluster import hosts, ports


multicast_ip = hosts.multicast
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

            # if multicast group receives a join message from a chat client, then the server leader executes the following:
            if hosts.leader == hosts.myIP and pickle.loads(data)[0] == 'JOIN':
                print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Client {address[0]} wants to join the chat room',
                      file=sys.stderr)
                # answer chat client with the current server leader
                message = pickle.dumps([hosts.leader, ''])
                sock.sendto(message, address)

            # messages between all server if leader crashes, server list or client list changes
            if len(pickle.loads(data)[0]) == 0:
                hosts.server_list.append(address[0]) if address[0] not in hosts.server_list else hosts.server_list
                sock.sendto('ack'.encode(unicode), address)
                hosts.network_changed = True

            elif pickle.loads(data)[1] and hosts.leader != hosts.myIP or pickle.loads(data)[3]:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                hosts.client_list = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {hosts.myIP}] All Data have been updated',
                      file=sys.stderr)
                server.printer()
                sock.sendto('ack'.encode(unicode), address)
                hosts.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                  file=sys.stderr)
