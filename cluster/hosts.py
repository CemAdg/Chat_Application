# this is for all hosts
import socket

# Get own Machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]
multicast = '224.3.29.71'

leader = ''
leader_crashed = ''
replica_crashed = ''
neighbour = ''
server_running = False
heartbeat_running = False
network_changed = False
server_list = []
connections = []

