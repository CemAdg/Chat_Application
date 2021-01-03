# this is for heartbeat

import socket
import sys
from time import sleep

from cluster import variable_list, leader_election


def start_heartbeat():
    #print(variable_list.server_list)
    variable_list.heartbeat_running = True
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        variable_list.neighbour = leader_election.start_leader_election(variable_list.server_list, variable_list.myIP)
        host_address = (variable_list.neighbour, variable_list.server_port)
        if variable_list.neighbour:
            print('\n[HEARTBEAT] sent',
                  file=sys.stderr)
            sleep(3)
            try:
                sock.connect(host_address)
                sleep(1)
                print(f'[HEARTBEAT] response by Neighbour {variable_list.neighbour}',
                      file=sys.stderr)
            except:
                variable_list.server_list.remove(variable_list.neighbour)
                if variable_list.leader == variable_list.neighbour:
                    variable_list.leader_crashed = True
                    variable_list.leader = variable_list.myIP
                    variable_list.network_changed = True
                    print(f'[HEARTBEAT] Server Leader {variable_list.neighbour} crashed')
                else:
                    variable_list.replica_crashed = 'True'
                    print(f'[HEARTBEAT] Server Replica {variable_list.neighbour} crashed')
            finally:
                sock.close()
