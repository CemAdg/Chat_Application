# this is for all hosts
import socket

# Get own Machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]
multicast = '224.0.0.0'

leader = ''
leader_crashed = ''
replica_crashed = ''
neighbour = ''
client_running = False
network_changed = False
server_list = []
client_list = []


