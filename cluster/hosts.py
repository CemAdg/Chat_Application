# this is for all hosts

# import modules
import socket

# get own machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

# connection variables
buffer_size = 1024
unicode = 'utf-8'

# global IP variables
multicast = '224.0.0.0'
leader = ''
neighbour = ''
server_list = []
client_list = []

# global state variables
client_running = False
network_changed = False
leader_crashed = ''
replica_crashed = ''
