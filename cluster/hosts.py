# this is for all hosts
import socket

# Get own Machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

multicast = '224.3.29.71'


# Server types
leader = ''
neighbour = ''

# Server Crash status
leader_crashed = ''
replica_crashed = ''

# General Server status
server_running = False
heartbeat_running = False
network_changed = False

# Lists
persons = []
client_list = []
server_list = []
connections = []
