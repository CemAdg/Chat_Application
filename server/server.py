import socket
from socket import SOCK_STREAM, AF_INET, socket
from threading import Thread
import time
from person import Person




#  Global Constants
# Bind the socket to the port
server_address = '127.0.0.1'
server_port = 10002
ADDR = (server_address, server_port)
MAX_CONNECTIONS = 10
# Buffer size
buffer_size = 1024

#Global Variables
persons = []
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(ADDR)
print('Server up and running at {}:{}'.format(server_address, server_port))

def broadcast(msg, name):
    for person in persons:
        client = person.client
        try:
            client.send(bytes(name + ": ", "utf8")+ msg )
        except Exception as e:
            print("[Exception]", e)




def client_communication(person):

    client = person.client
    # get persons name
    name = client.recv(buffer_size).decode("utf8")
    person.set_name(name)
    msg = bytes(f"{name} has joined the chat!", "utf8")
    broadcast(msg, "") # broadcast welcome message

    while True:
        msg = client.recv(buffer_size) # constantly waits for messages

        if msg == bytes("quit", "utf8"):
            client.close()
            persons.remove(person)
            broadcast(bytes(f"{name} has left the chat...", "utf8"), "")
            print(f"[DISCONNECTED] {name} disconnected")
            break
        else:
            broadcast(msg, name+": ")
            print(f"{name}: ", msg.decode("utf8"))


def wait_for_connection():
    while True:
        try:
            client, addr = server_socket.accept()
            person = Person(addr, client)
            persons.append(person)
            print(f"[CONNECTION] {addr} connected to the server at {time.time()}")
            Thread(target=client_communication, args=(person,)).start()
        except Exception as e:
            print("[Exception]", e)
            break

    print("SERVER CRASHED")


if __name__ == "__main__":
    while True:
        server_socket.listen(MAX_CONNECTIONS)  # listen for connections
        print("Waiting for connection...")
        ACCEPT_THREAD = Thread(target=wait_for_connection)
        ACCEPT_THREAD.start()
        ACCEPT_THREAD.join()
        server_socket.close()
