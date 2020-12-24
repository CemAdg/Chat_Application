# IMPORTS
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread
from person import Person
import time

# GLOBAL CONSTANTS
SERVER = socket(AF_INET, SOCK_DGRAM)  # create a socket to get machine address
SERVER.connect(("8.8.8.8", 80))
HOST = SERVER.getsockname()[0]  # gets the ipv4 address from the machine
PORT = 1000
BUFFER_SIZE = 1024
ADDR = ('localhost', 5000)
MAX_CONNECTIONS = 10
FORMAT = "utf8"


# GLOBAL VARIABLES
persons = []


SERVER = socket(AF_INET, SOCK_STREAM)  # create a socket
SERVER.bind(ADDR)  # binding the socket


def broadcast(msg, name):  # broadcast Function
    """
    send new messages to all clients
    :param msg: bytes
    :param name: str
    :return: None
    """
    for person in persons:  # person list iteration
        client = person.client
        try:
            client.send(bytes(name, FORMAT) + msg)
        except Exception as e:
            print("[EXCEPTION", e)


def client_communication(person):  # tmp_client communication Function
    """
    Thread to handle all messages from tmp_client
    :param person: Person
    :return: None
    """
    client = person.client

    name = client.recv(BUFFER_SIZE).decode(FORMAT)  # get person name
    msg = bytes(f"{name} has joined the chat!", FORMAT)
    broadcast(msg, "")  # broadcast welcome message

    while True:  # loop while tmp_client connected
        msg = client.recv(BUFFER_SIZE)
        if msg == bytes("{quit}", FORMAT):  # if person left the session
            client.close()
            persons.remove(person)  # remove person from persons list
            broadcast(bytes(f"{name} has left the chat...", FORMAT), "")
            print(f"[DISCONNECTED] {name} disconnected")
            break
        else:
            broadcast(msg, name + ": ")
            print(f"{name}: ", msg.decode(FORMAT))


def wait_for_connection():  # wait for connection Function
    """
    Wait for connection from new clients, start new thread once connected
    :param SERVER: SOCKET
    :return: None
    """
    while True:  # loop if connection available
        try:  # try to get address from tmp_client and start a Thread
            client, addr = SERVER.accept()  # get tmp_client address
            person = Person(addr, client)
            persons.append(person)  # append person to persons list
            print(f"[CONNECTION] {addr} connected to the tmp_server at {time.time()}")
            Thread(target=client_communication, args=(person,)).start()  # starting Thread with tmp_client connection
        except Exception as e:  # print an exception if getting tmp_client information fails
            print("[EXCEPTION]", e)
            break

    print("SERVER CRASHED")


if __name__ == "__main__":  # is true if the process is main
    SERVER.listen(MAX_CONNECTIONS)  # listen for connection
    print("[STARED] Waiting for connection...")
    ACCEPT_THREAD = Thread(target=wait_for_connection)  # starting thread for tmp_server
    ACCEPT_THREAD.start()  # starting thread tmp_server
    ACCEPT_THREAD.join()  # joining thread tmp_server
    SERVER.close()  # closing tmp_server
