import socket
import struct
import sys
import pickle

from cluster import hosts, ports


multicast_ip = hosts.multicast
server_address = ('', ports.multicast)
client_address = ('', ports.multicast_client)


buffer_size = 1024
unicode = 'utf-8'

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
            elif pickle.loads(data)[1] and hosts.leader != hosts.myIP or pickle.loads(data)[3]:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                print(f'[MULTICAST RECEIVER {hosts.myIP}] All Data have been updated',
                      file=sys.stderr)

            sock.sendto('ack'.encode(unicode), address)
            hosts.network_changed = True
        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                  file=sys.stderr)
            break

def starting_client_multicast_receiver():
    # Bind to the Client address
    sock_client.bind(client_address)
    # Tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock_client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Starting UDP Socket for chat joining requests and listening on Port {ports.multicast_client}',
          file=sys.stderr)

    # Receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(buffer_size)

            print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Received data from {address[0]}',
                  file=sys.stderr)

            if hosts.server_leader == hosts.myIP and pickle.loads(data)[0] == "JOIN":
                print(
                    f'[MULTICAST RECEIVER {hosts.myIP}] Client {pickle.loads(data)[1]} - {address} wants to join the chat',
                    file=sys.stderr)
                # add chat client in client_list (including address and client name)
                hosts.client_list.append(address[0])
                # answer chat client with the current client list and the server leader
                message = pickle.dumps([hosts.client_list, hosts.server_leader])
                sock.sendto(message, address)

                # set network_changed to true, so every server replica gets the updated client list
                hosts.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                  file=sys.stderr)
            break