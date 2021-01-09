# this is a Multicast Receiver

# import Modules
import socket
import sys
import struct
import pickle

from cluster import hosts, ports

# get the Multicast IP from cluster.hosts
# get the port used for Multicast from cluster.ports
multicast_ip = hosts.multicast
server_address = ('', ports.multicast)

# create the UDP Socket for Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# used from Servers
def starting_multicast_receiver():

    # bind the Server address
    sock.bind(server_address)

    # tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Starting UDP Socket and listening on Port {ports.multicast}',
          file=sys.stderr)

    # receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(hosts.buffer_size)
            print(f'\n[MULTICAST RECEIVER {hosts.myIP}] Received data from {address}\n',
                  file=sys.stderr)

            # used from Server Leader if a join message was sent from a Chat Client
            if hosts.leader == hosts.myIP and pickle.loads(data)[0] == 'JOIN':

                # answer Chat Client with Server Leader address
                message = pickle.dumps([hosts.leader, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {hosts.myIP}] Client {address} wants to join the Chat Room\n',
                      file=sys.stderr)

            # used from Server Leader if a Server Replica joined
            if len(pickle.loads(data)[0]) == 0:
                hosts.server_list.append(address[0]) if address[0] not in hosts.server_list else hosts.server_list
                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.network_changed = True

            # used from Server Replicas to update the own variables or if a Server Replica crashed
            elif pickle.loads(data)[1] and hosts.leader != hosts.myIP or pickle.loads(data)[3]:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                hosts.client_list = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {hosts.myIP}] All Data have been updated',
                      file=sys.stderr)

                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.myIP}] Closing UDP Socket',
                  file=sys.stderr)
