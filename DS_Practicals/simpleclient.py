import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server application IP address and port
server_address = '127.0.0.1'
server_port = 10001

# Buffer size
buffer_size = 1024

# Message sent to testserver
message = 'Hi testserver!'

try:
    # Send data to testserver
    client_socket.sendto(message.encode(), (server_address, server_port))
    print('Sent to testserver: ', message)

    # Receive response from testserver
    print('Waiting for response...')
    data, server = client_socket.recvfrom(buffer_size)
    print('Received message from testserver: ', data.decode())

finally:
    client_socket.close()
    print('Socket closed')
