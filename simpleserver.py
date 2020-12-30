import socket


# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server application IP address and port
server_address = socket.gethostname()
server_port = 10001

# Buffer size
buffer_size = 1024

# Message to be sent to tmp_client
message = 'Hi tmp_client! Nice to connect with you!'

# Bind socket to port
server_socket.bind((server_address, server_port))
print('Server up and running at {}:{}'.format(server_address, server_port))

while True:
    print('\nWaiting to receive message...\n')

    # Receive message from tmp_client
    data, address = server_socket.recvfrom(buffer_size)
    print('Received message from tmp_client: ', address)
    print('Message: ', data.decode())

    if data:
        # Send message to tmp_client
        message = input("Please enter a string:\n")
        server_socket.sendto(str.encode(message), address)
        print('Replied to tmp_client: ', message)
