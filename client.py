import socket
import threading
from time import sleep
from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat

# leader_address = ('19.10.19.20', ports.server)
buffer_size = 1024
unicode = 'utf-8'


def send_message():
    while True:
        try:
            sock.send(input("").encode(unicode))

            """
            if not data:
                print("\nChat server currently not available. Please wait for reconnection with new server leader")
                sock.close()
                sleep(5)
                send_multicast.sending_join_chat_request_to_multicast()
                # assign new leader address
                leader_address = (hosts.leader, ports.server)
                sock.connect(leader_address)
                #break
            """
        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break


def receive_message():
    hosts.client_running = True
    while True:
        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))

            if not data:
                print("\nChat server currently not available. Please wait for reconnection with new server leader")
                sock.close()
                """
                #sock.shutdown()

                # start socket again
                #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # get new server leader
                sleep(8)
                send_multicast.sending_join_chat_request_to_multicast()

                # assign and connect to new leader address
                sleep(2)
                leader_address = (hosts.leader, ports.server)

                sock.connect(leader_address)
                #break
                """
                sleep(10)
                # Reconnect to new server leader
                connect()


        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break


def connect():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # send join request to multicast for receiving server leader address
    send_multicast.sending_join_chat_request_to_multicast()

    # assign server leader address
    leader_address = (hosts.leader, ports.server)

    print(f'This is the server leader: {leader_address}')

    # connect to server leader
    sock.connect(leader_address)


def new_thread(target, args, join):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()
    t.join() if join else None


if __name__ == '__main__':
    print("You try to join the chat room.")

    name = input("Please enter your name:")

    # Set up socket and start connection
    connect()

    while True:
        new_thread(send_message, (), False) if not hosts.client_running else None
        new_thread(receive_message, (), False) if not hosts.client_running else None

"""
    while True:
        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))
        except KeyboardInterrupt:
            sock.close()
            print("\nClient closed")
            break
"""
