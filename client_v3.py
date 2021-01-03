# this is a client

import socket
import sys
import threading

from time import sleep

from cluster import app_init, receive_multicast, send_multicast, leader_election, heartbeat



# Send join message to multicast address and receive server leader address
# Connect to server leader address
# listen multicast for server leader crash messages: receive new server leader address
# Disconnect crashed server and connect to new leader
