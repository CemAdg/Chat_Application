# this is a Client

# import Modules
import socket
import threading
import os

from time import sleep
from cluster import hosts, ports, send_multicast


# standardized for creating and starting Threads
def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


# function for sending messages to the Server
def send_message():
    global sock

    while True:
        message = input("")

        try:
            sock.send(message.encode(hosts.unicode))

        except Exception as e:
            print(e)
            break


# function for receiving messages from the Server
def receive_message():
    global sock

    while True:

        try:
            data = sock.recv(hosts.buffer_size)
            print(data.decode(hosts.unicode))

            # if connection to server is lost (in case of server crash)
            if not data:
                print("\nChat server currently not available."
                      "Please wait 3 seconds for reconnection with new server leader.")
                sock.close()
                sleep(3)

                # Start reconnecting to new server leader
                connect()

        except Exception as e:
            print(e)
            break


# function for creating Client socket and establishing connection to Server Leader
def connect():
    global sock

    # creating TCP Socket for Client
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # send a join request to Multicast Address for receiving the current Server Leader address
    # if there is no response from the Server Leader, value False will be returned
    server_exist = send_multicast.sending_join_chat_request_to_multicast()

    if server_exist:
        # assign Server Leader address
        leader_address = (hosts.leader, ports.server)
        print(f'This is the server leader: {leader_address}')

        # connect to Server Leader
        sock.connect(leader_address)
        sock.send('JOIN'.encode(hosts.unicode))
        print("You joined the Chat Room.\nYou can start chatting.")

    # if there is no Server available, exit the script
    else:
        print("Please try to join later again.")
        os._exit(0)


# main Thread
if __name__ == '__main__':
    try:
        print("You try to join the chat room.")

        # Connect to Server Leader
        connect()

        # Start Threads for sending and receiving messages from other chat participants
        new_thread(send_message, ())
        new_thread(receive_message, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou left the chatroom")
