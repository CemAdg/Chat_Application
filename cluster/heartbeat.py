# this is for Heartbeat

# import Modules
import socket
import sys

from time import sleep
from cluster import hosts, ports, leader_election


# used from Server
def start_heartbeat():
    while True:
        # create the TCP Socket for Heartbeat
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.5)

        # get own Server Neighbour by using Leader Election algorithm
        hosts.neighbour = leader_election.start_leader_election(hosts.server_list, hosts.myIP)
        host_address = (hosts.neighbour, ports.server)


        # only executed if a Neighbour is available to whom the Server can establish a connection
        if hosts.neighbour:
            sleep(3)

            # Heartbeat is realized by connecting to the Neighbour
            try:
                sock.connect(host_address)
                print(f'[HEARTBEAT] Neighbour {hosts.neighbour} response',
                      file=sys.stderr)

            # if connecting to Neighbour was not possible, the Heartbeat failed -> Neighbour crashed
            except:
                # remove crashed Neighbour from Server List
                hosts.server_list.remove(hosts.neighbour)

                # used if the crashed Neighbour was the Server Leader
                if hosts.leader == hosts.neighbour:
                    print(f'[HEARTBEAT] Server Leader {hosts.neighbour} crashed',
                          file=sys.stderr)
                    hosts.leader_crashed = True

                    # assign own IP address as new Server Leader
                    hosts.leader = hosts.myIP
                    hosts.network_changed = True

                # used if crashed Neighbour was a Server Replica
                else:
                    print(f'[HEARTBEAT] Server Replica {hosts.neighbour} crashed',
                          file=sys.stderr)
                    hosts.replica_crashed = 'True'

            finally:
                sock.close()
