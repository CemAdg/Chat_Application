# this is for Server Leader Election

import socket

server_list = ['0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.4']
leader_server = '0.0.0.3'


def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    # print(sorted_binary_ring)
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    print(sorted_ip_ring)
    return sorted_ip_ring


def get_neighbour(members, current_member_ip, direction='left'):
    current_member_index = members.index(current_member_ip) if current_member_ip in members else -1
    if current_member_index != -1:
        if direction == 'left':
            if current_member_index + 1 == len(members):
                return members[0]
            else:
                return members[current_member_index + 1]
        else:
            if current_member_index - 1 == 0:
                return members[0]
            else:
                return members[current_member_index - 1]
    else:
        return None


def start_leader_election(server_list, leader_server):
    ring = form_ring(server_list)
    neighbour = get_neighbour(ring, leader_server, 'right')
    print(neighbour)


start_leader_election(server_list, leader_server)