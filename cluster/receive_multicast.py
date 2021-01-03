import socket
import struct
import sys
import pickle

from cluster import app_init


multicast_ip = app_init.multicast_ipaddress
server_address = ('', app_init.multicast_port)
buffer_size = 1024
unicode = 'utf-8'

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def starting_multicast_receiver():
    # Tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the Server address
    sock.bind(server_address)

    print(f'\n[MULTICAST RECEIVER {app_init.myIP}] Starting UDP Socket and listening on Port {app_init.multicast_port}',
          file=sys.stderr)

    # Receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(buffer_size)

            print(f'\n[MULTICAST RECEIVER {app_init.myIP}] Received data from {address[0]}',
                  file=sys.stderr)

            if len(pickle.loads(data)[0]) == 0:
                app_init.server_list.append(address[0]) if address[0] not in app_init.server_list else app_init.server_list
            elif pickle.loads(data)[1] and app_init.server_leader != app_init.myIP or pickle.loads(data)[3]:
                app_init.server_list = pickle.loads(data)[0]
                app_init.server_leader = pickle.loads(data)[1]
                print(f'[MULTICAST RECEIVER {app_init.myIP}] All Data have been updated',
                      file=sys.stderr)

            sock.sendto('ack'.encode(unicode), address)
            app_init.network_changed = True
        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {app_init.myIP}] Closing UDP Socket',
                  file=sys.stderr)
            break
