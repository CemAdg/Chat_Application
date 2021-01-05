import socket
import threading
from time import sleep
from cluster import hosts, ports, receive_multicast, send_multicast, leader_election, heartbeat

# leader_address = ('19.10.19.20', ports.server)
buffer_size = 1024
unicode = 'utf-8'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_message():
    global sock

    while True:
        message = input("")
        #sock = getGlobalSock()

        try:
            sock.send(message.encode(unicode))

        except OSError as e:
            print(e)
            #sock.close()
            #sock.shutdown(socket.SHUT_RDWR)

        except KeyboardInterrupt:
            #sock.close()
            print("\nClient closed")
            break


def receive_message():
    global sock
    hosts.client_running = True
    while True:

        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))

            if not data:
                print("\nChat server currently not available. Please wait 10 seconds for reconnection with new server leader.")
                sock.close()
                #sock.shutdown(socket.SHUT_RDWR)

                sleep(10)
                # Reconnect to new server leader
                connect()
                sleep(2)
                sock.send(("vallah nein").encode(unicode))


        except KeyboardInterrupt:
            #sock.close()
            print("\nClient closed")
            break

def getGlobalSock():
    print("Get new sock")
    global sock
    return sock

def connect():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(sock)

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
