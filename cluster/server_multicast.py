import socket
import struct
from time import sleep

from cluster.ports import MULTICAST_PORT_SERVER


def sendMulticastMessage():
    leader_server_found = False
    message = ('This is a multicast msg')
    #multicast_group = ('224.3.29.71', MULTICAST_PORT_SERVER)
    multicast_group = ('224.0.0.1', MULTICAST_PORT_SERVER)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data. (in sec flaot)
    sock.settimeout(2)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    while (not leader_server_found):
        try:
            # Send data to the multicast group
            print('Sending multicast msg to discover leader server')
            sent = sock.sendto(message.encode(), multicast_group)
            # Look for responses from all recipients
            while True:
                print('Server multicast: Waiting to receive respond to sent multicast message from the leader')
                try:
                    data, server_addr = sock.recvfrom(1024)  # receive 128 bytes at once
                    if data.decode() == "True":
                        print('received "%s" from %s' % (data.decode(), server_addr))
                        leader_server_found = True  # Leader Server discovered stop multicasting
                        break
                except socket.timeout:
                    #print('Timed out, no more responses')
                    break
        except KeyboardInterrupt:  # on CTRL-C
            break

        except:
            print("Failed to send multicast message")

        if leader_server_found==False:  #send another multicast after 2 seconds only when leader is not found
            sleep(2)