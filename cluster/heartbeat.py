# this is for heartbeat

import socket

from cluster import hosts, ports, leader_election


def start_heartbeat():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    neighbour = leader_election.start_leader_election(hosts.server_list, hosts.myIP)
    host_address = (neighbour, ports.server)
    sock.settimeout(2)
    try:
        sock.connect(host_address)
        return True
    except Exception as e:
        print(e)
        return False
