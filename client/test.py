from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# Global Constants
server_address = '127.0.0.1'
server_port = 10002
ADDR = (server_address, server_port)
buffer_size = 1024

# Global Vairables
messages = []

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


def recieve_messages():
    while True:
        try:
            msg = client_socket.recv(buffer_size).decode()
            messages.append(msg)
            print(msg)
        except Exception as e:
            print("[Exception]", e)
            break

def send_message(msg):
        client_socket.send(bytes(msg, "utf8"))
        if msg == "quit":
            client_socket.close()

receive_thread = Thread(target=recieve_messages)
receive_thread.start()

send_message("Cem")
send_message("hello")
send_message("my name is Cem")
send_message("I like to play football")
send_message("quit")