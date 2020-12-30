import socket
import multiprocessing
import os


def send_message(s_address, s_port):
    try:
        # Create a UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Message sent to testserver
        message = 'Hi from ' + str(os.getpid()) + ' at ' + s_address + ':' + str(s_port)

        # Send data
        client_socket.sendto(str.encode(message), (s_address, s_port))
        print('Sent to testserver: ', message)

        # Receive response from testserver
        print('Waiting for response...')
        data, server = client_socket.recvfrom(1024)
        print('Received message: ', data.decode())

    finally:
        client_socket.close()
        print('Socket closed')


if __name__ == '__main__':

    # Server application IP address and port
    server_address = '127.0.0.1'
    server_port = 10001

    for i in range(3):
        # Spawn three testclient processes
        p = multiprocessing.Process(target=send_message, args=(server_address, server_port))
        p.start()
        p.join
