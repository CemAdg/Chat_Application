# this is a client

import socket
import sys
import threading

from time import sleep

from cluster import hosts, receive_multicast, send_multicast, leader_election, heartbeat

localhost_address = ("localhost", 5500)
buffer_size = 1024
unicode = 'utf-8'

join_status = ''

messages = []

# Create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def receive_messages():
    """
    receive messages from server and prints them to the terminal of chat participants
    :return: None
    """

    while True:
        try:
            msg = client_socket.recv(buffer_size)
            # received messages from the server will be cached in .messages object
            messages.append(msg.decode())

            for msg in messages:
                print(msg)

            messages = []

            if join_status == False:
                break

        except Exception as e:
            print("[EXCEPTION]", e)
            break


def send_message():
    """
    send messages to server
    :param msg: str
    :return: None
    """
    while True:
        sleep(0.1)
        msg = (input(), client_membername)

        try:
            client_socket.send(bytes(msg.encode(), unicode))
            if msg[0] == "{quit}":
                client_socket.close()
                print("You left the chat!")
                join_status = False
                break
        except Exception as e:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.connect(host_address)
            print(e)

if __name__ == "__main__":

    print("Hello, you're trying to join the chat room. You can leave the chat again by entering {quit}.")
    client_membername = input("Please enter your name for joining: ")

    # Send join message to multicast address and receive server leader address
    send_multicast.send_join_chat_message_to_multicast(client_membername)

    # Connect to server leader
    host_address = (hosts.server_leader, hosts.server_port)
    client_socket.connect(host_address)
    join_status = True

    threading.Thread(target=send_message).start()
    threading.Thread(target=receive_messages).start()



# listen multicast for server leader crash messages: receive new server leader address
# Disconnect crashed server and connect to new leader
