# this is for heartbeat

import socket
import sys
from time import sleep

from cluster import app_init, leader_election


def start_heartbeat():
    #print(variable_list.server_list)
    app_init.heartbeat_running = True
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        app_init.server_neighbour = leader_election.start_leader_election(app_init.server_list, app_init.myIP)
        host_address = (app_init.server_neighbour, app_init.server_port)
        if app_init.server_neighbour:
            print('\n[HEARTBEAT] sent',
                  file=sys.stderr)
            sleep(3)
            try:
                sock.connect(host_address)
                sleep(1)
                print(f'[HEARTBEAT] response by Neighbour {app_init.server_neighbour}',
                      file=sys.stderr)
            except:
                app_init.server_list.remove(app_init.server_neighbour)
                if app_init.server_leader == app_init.server_neighbour:
                    app_init.server_leader_crashed = True
                    app_init.server_leader = app_init.myIP
                    app_init.network_changed = True
                    print(f'[HEARTBEAT] Server Leader {app_init.server_neighbour} crashed')
                else:
                    app_init.server_replica_crashed = 'True'
                    print(f'[HEARTBEAT] Server Replica {app_init.server_neighbour} crashed')
            finally:
                sock.close()
