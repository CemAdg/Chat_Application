from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread

SERVER = socket(AF_INET, SOCK_DGRAM)  # create a socket to get machine address
SERVER.connect(("8.8.8.8", 80))
HOST = SERVER.getsockname()[0]  # gets the ipv4 address from the machine
PORT = 10000
BUFFER_SIZE = 1024
HOST_ADDRESS = ('19.10.19.20', PORT)
FORMAT = "utf-8"

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(HOST_ADDRESS)

SERVER.listen()

clients = []
aliases = []


def broadcast(message, sender):
    for client in clients:
        if sender != client:
            client.send(message)


def handle_client(client):
    while True:
        message = (f'{aliases[clients.index(client)]}: ').encode(FORMAT) + client.recv(BUFFER_SIZE)
        broadcast(message, client)

    else:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        alias = aliases[index]
        print(f'Connection lost with {alias}')
        broadcast(f'{alias} has left the chat room'.encode(FORMAT), client)
        aliases.remove(alias)


def receive():
    while True:
        print(f'Server is running and listening @ {HOST_ADDRESS}')
        client, address = SERVER.accept()
        client.send('alias?'.encode(FORMAT))
        alias = client.recv(BUFFER_SIZE).decode(FORMAT)
        aliases.append(alias)
        clients.append(client)
        print(f'Connection is established with {str(address)}')
        print(f'The Alias of this Client is {alias}')
        broadcast(f'{alias} has connected to the chat room'.encode(FORMAT), client)
        client.send('You are now connected'.encode(FORMAT))
        thread = Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == "__main__":
    receive()
