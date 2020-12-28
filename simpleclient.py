import socket

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server TWT application IP address and port
server_address = '127.0.0.1'
server_port = 10001

# Buffer size
buffer_size = 1024

# Message sent to tmp_server
message = 'Hi tmp_server!'
value = input("Please enter a string:\n")
message = f'{message}\n{value}'
#print(f'You entered {message}')  format alternative

while True:

    # Send data to tmp_server
    client_socket.sendto(message.encode(), (server_address, server_port))
    print('Sent to tmp_server: ', message)

    # Receive response from tmp_server
    print('Waiting for response...')
    data, server = client_socket.recvfrom(buffer_size)
    print('Received message from tmp_server: ', data.decode())

    if data.decode() == 'Geh raus':
        break

    value = input("Please enter a string:\n")
    message = value

#finally:
#    client_socket.close()
#    print('Socket closed')
