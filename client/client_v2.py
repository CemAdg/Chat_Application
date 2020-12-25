from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Lock
import time


class Client:
    """
    for communication with server
    """
    HOST = "localhost"
    PORT = 5500
    ADDR = (HOST, PORT)
    BUFSIZ = 1024

    def __init__(self, name):
        """
        Init object and send name to server
        :param name: str
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)
        self.messages = []
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()
        self.send_message(name)

    def receive_messages(self):
        """
        receive messages from server
        :return: None
        """
        while True:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode()
                # received messages from the server will be cached in .messages object
                self.messages.append(msg)

            except Exception as e:
                print("[EXCEPTION]", e)
                break

    def send_message(self, msg):
        """
        send messages to server
        :param msg: str
        :return: None
        """
        try:
            self.client_socket.send(bytes(msg, "utf8"))
            if msg == "{quit}":
                self.client_socket.close()
                print("You left the chat!")
        except Exception as e:
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.ADDR)
            print(e)

    def get_messages(self):
        """
        :returns a list of str messages
        :return: list[str]
        """
        messages_copy = self.messages[:]

        # after getting the new messages from the server (which are saved in the messages attribute of the client object), the cache for all messages will be cleared
        # this ensures that only the new messages will be printed to the UI with the messages_copy variable
        self.messages = []

        return messages_copy

    def disconnect(self):
        self.send_message("{quit}")


##########################################
####### GUI Front End Replacement: #######
##########################################

def UI_show_messages():
    """
    updates the local list of messages
    :return: None
    """
    msgs = []

    run = True
    while run:
        time.sleep(0.1)  # update every 1/10 of a second
        new_messages = c.get_messages()  # get any new messages from client
        msgs.extend(new_messages)  # add to local list of messages

        for msg in new_messages:  # display new messages
            print(msg)

            if msg == "{quit}":
                run = False
                break


def UI_send_messages():
    """
       provides input-UI for sending chat messages
       :return: None
    """

    run = True
    while run:
        time.sleep(0.1)  # update every 1/10 of a second
        msg_body = input()
        message = c.send_message(msg_body)

        if msg_body == "{quit}":
            run = False
            break


if __name__ == "__main__":
    name = input("You're trying to join the chat room. Please first enter your name: ")
    c = Client(name)

    Thread(target=UI_show_messages).start()
    Thread(target=UI_send_messages).start()