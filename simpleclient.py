import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Server application IP address and port
server_address = '19.10.19.20'
server_port = 10001

# Buffer size
buffer_size = 1024

# Message sent to tmp_server
value = "Please enter a string"
message = f'\n{value}'
#print(f'You entered {message}')  format alternative
client_socket.connect((server_address, server_port))


while True:

    try:
        # Send data to tmp_server
        client_socket.send(message.encode('utf-8'))

        # Receive response from tmp_server
        print('Waiting for response...')
        data = client_socket.recv(buffer_size)
        print('Received message from tmp_server: ', data.decode('utf-8'))

        """if data.decode() == 'Geh raus':
            break"""

        value = input("Please enter a string:\n")
        message = value

    except KeyboardInterrupt:
        client_socket.close()
        print('Socket closed')
