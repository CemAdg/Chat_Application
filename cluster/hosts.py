# this is for all hosts
import socket

# Get own Machine IP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
myIP = sock.getsockname()[0]

leader = ''
leader_crashed = False
non_leader_crashed = False
server_list = []
connections = []

