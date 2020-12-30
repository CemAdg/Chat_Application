import multiprocessing
import socket
import os


class Server(multiprocessing.Process):
    def __init__(self, server_socket, received_data, client_address):
        super(Server, self).__init__()
        self.server_socket = server_socket
        self.received_data = received_data
        self.client_address = client_address

    # Override run method
    def run(self):
        # Message to be sent to testclient
        message = 'Hi ' + self.client_address[0] + ':' + str(self.client_address[1]) + '. This is testserver ' + str(os.getpid())
        # Send message to testclient
        self.server_socket.sendto(str.encode(message), self.client_address)
        print('Sent to testclient: ', message)


if __name__ == "__main__":
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Server application IP address and port
    server_address = '127.0.0.1'
    server_port = 10001

    # Buffer size
    buffer_size = 1024

    # Bind socket to address and port
    server_socket.bind((server_address, server_port))
    print('Server up and running at {}:{}'.format(server_address, server_port))

    while True:
        # Receive message from testclient
        data, address = server_socket.recvfrom(buffer_size)
        print('Received message \'{}\' at {}:{}'.format(data.decode(), address[0], address[1]))
        # Create a testserver process
        p = Server(server_socket, data, address)
        p.start()
        p.join()
