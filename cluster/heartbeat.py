# this is for heartbeat

import socket
import sys
from time import sleep

from cluster import hosts, ports, leader_election


def start_heartbeat():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hosts.neighbour = leader_election.start_leader_election(hosts.server_list, hosts.myIP)
        host_address = (hosts.neighbour, ports.server)
        if hosts.neighbour:
            print('\n[HEARTBEAT]', file=sys.stderr)
            sleep(3)
            try:
                sock.connect(host_address)
            except Exception as e:
                hosts.server_list.remove(hosts.neighbour)
                if hosts.leader == hosts.neighbour:
                    hosts.leader_crashed = True
                    hosts.leader = hosts.myIP
                    hosts.network_changed = True
                else:
                    hosts.non_leader_crashed = True
                print(f'[FAILED SERVER] {hosts.neighbour} crashed')
                print(e)
            finally:
                sock.close()
