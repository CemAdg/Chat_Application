import socket
import threading
from time import sleep
from cluster import hosts, ports, send_multicast

buffer_size = 1024
unicode = 'utf-8'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_message():
    global sock

    while True:
        message = input("")

        try:
            sock.send(message.encode(unicode))

        except Exception as e:
            print(e)


def receive_message():
    global sock

    while True:

        try:
            data = sock.recv(buffer_size)
            print(data.decode(unicode))

            if not data:
                print("\nChat server currently not available."
                      "Please wait 3 seconds for reconnection with new server leader.")
                sock.close()

                sleep(3)
                # Reconnect to new server leader
                connect()

        except Exception as e:
            print(e)


def connect():
    global sock

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # send join request to multicast for receiving server leader address
    send_multicast.sending_join_chat_request_to_multicast()

    # assign server leader address
    leader_address = (hosts.leader, ports.server)

    print(f'This is the server leader: {leader_address}')

    # connect to server leader
    sock.connect(leader_address)

    print("You joined the chatroom.\nYou can start chatting.")


def new_thread(target, args):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    try:
        print("You try to join the chat room.")

        connect()
        new_thread(send_message, ())
        new_thread(receive_message, ())

        while True:
            pass
    except KeyboardInterrupt:
        print("\nYou left the chatroom")
