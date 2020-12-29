import socket
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath("")) #root path of project  --> .../OnlineShop/
sys.path.append(ROOT_DIR)    #Add path to project root otherwise imports will fail
from cluster.ports import SERVER_LEADER_ELECTION_PORT

neighbour = ''

def form_ring(members):
    sorted_binary_ring = sorted([socket.inet_aton(member) for member in members])
    #print(sorted_binary_ring)
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
    #print(sorted_ip_ring)
    return sorted_ip_ring

def get_neighbour(members, current_member_ip, direction='left'):
    current_member_index = members.index(current_member_ip) if current_member_ip in members else -1

    if current_member_index != -1:
        if direction == 'left':
            if current_member_index == 0:
                return members[-1]
            else:
                return members[- 1]
        else:    #right neighbour
            if current_member_index  == len(members)-1: #len -1 since list index starts with 0
                return members[0]
            else:
                return members[current_member_index + 1]
    else:
        return None

def sendElectionmessage(election_msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create TCP socket
    s.settimeout(2)  # set timeout for every socket to 1 second
    try:
        s.connect((neighbour, SERVER_LEADER_ELECTION_PORT))  # Connect each socket to ip adress and UNICAST Port
    except:
        print('cant connect to neighbour')
    try:
        #s.connect((neighbour, SERVER_LEADER_ELECTION_PORT))  # Connect each socket to ip adress and UNICAST Port
        print('Sending election message: ',election_msg ,'to: ',neighbour)
        message = election_msg            #first round it is the own ip
        s.send(message.encode())
    except:
        print('cant send msg to neighbour')
    finally:
        s.close()

    pass


def startElection(serverlist,host_ip_address):
    members = []
    members.append(host_ip_address)

    for x in range(len(serverlist)):
        connection_and_leader = serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
        server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
        ip, port = server_adress  # split up server_adress into ip adress and port
        members.append(ip)        #Add IP adress to memberslist

    #print('Memberlist: ',members)

    #members = ['192.168.0.1', '130.234.204.2', '130.234.203.2', '130.234.204.1', '182.4.3.111']
    if len(serverlist)==1:
        global neighbour
        connection_and_leader = serverlist[0]
        server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
        ip, port = server_adress
        neighbour=ip       #in this case only one member is in the list which is the only neighbor
        print('Serverlist consists 1 element. Only one neighbour.')
        sendElectionmessage(host_ip_address)   #start election with sending own ip
    else:
        ring = form_ring(members)
        neighbour = get_neighbour(ring, host_ip_address, 'right')
        print('Ring of Hosts:',ring,'My IP:',host_ip_address,'My neighbour:',neighbour)
        sendElectionmessage(host_ip_address)

