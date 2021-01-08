# this is for heartbeat

import socket
import sys
from time import sleep

from cluster import hosts, ports, leader_election


def start_heartbeat():
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(0.5)
        hosts.neighbour = leader_election.start_leader_election(hosts.server_list, hosts.myIP)
        host_address = (hosts.neighbour, ports.server)
        print(f'\n{hosts.server_list}\n',
              file=sys.stderr) if len(hosts.server_list) > 1 else None
        if hosts.neighbour:
            sleep(3)
            try:
                sock.connect(host_address)
                print(f'[HEARTBEAT] Neighbour {hosts.neighbour} response',
                      file=sys.stderr)
            except:
                hosts.server_list.remove(hosts.neighbour)
                if hosts.leader == hosts.neighbour:
                    hosts.leader_crashed = True
                    hosts.leader = hosts.myIP
                    hosts.network_changed = True
                    print(f'[HEARTBEAT] Server Leader {hosts.neighbour} crashed',
                          file=sys.stderr)
                else:
                    hosts.replica_crashed = 'True'
                    print(f'[HEARTBEAT] Server Replica {hosts.neighbour} crashed',
                          file=sys.stderr)
            finally:
                sock.close()
