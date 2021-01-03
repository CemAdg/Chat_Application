# Variable Collection
import socket

# Get own Machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

#multicast_ipaddress = '224.3.29.71'
multicast_ipaddress = '224.0.0.1'

# Ports
multicast_port = 10000
server_port = 10001

# Server types
server_leader = ''
server_neighbour = ''

# Server Crash status
server_leader_crashed = ''
server_replica_crashed = ''

# General Server status
server_running = False
heartbeat_running = False
network_changed = False

# Lists
client_list = []
server_list = []
connections = []

