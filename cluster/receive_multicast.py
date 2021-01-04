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

            # if multicast group receives a join message from a chat client, then the server leader executes the following:
            if app_init.server_leader == app_init.myIP and pickle.loads(data)[0] == "JOIN":
                print(f'[MULTICAST RECEIVER {app_init.myIP}] Client {pickle.loads(data)[1]} - {address} wants to join the chat',
                      file=sys.stderr)
                # add chat client in client_list (including address and client name)
                app_init.client_list.append(address[0])
                # answer chat client with the current client list and the server leader
                message = pickle.dumps([app_init.client_list, app_init.server_leader])
                sock.sendto(message, address)

                # set network_changed to true, so every server replica gets the updated client list
                app_init.network_changed = True

            # messages between server
            elif len(pickle.loads(data)[0]) == 0:
                app_init.server_list.append(address[0]) if address[0] not in app_init.server_list else app_init.server_list
                sock.sendto('ack'.encode(unicode), address)
                app_init.network_changed = True

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
