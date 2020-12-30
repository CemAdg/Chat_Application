import socket
import threading
import sys
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 10000
hAddress = (host, port)
bSize = 1024
unicode = 'utf-8'
leader = True

if __name__ == '__main__':
    sock.bind(hAddress)
    print(f'Server is running and listening on IP {host} with PORT {port}', file=sys.stderr)

    sock.listen(1)

    connections = []


    def handler(c, a):
        while True:
            data = c.recv(bSize)
            if not data:
                print(f'{a[0]}:{a[1]} disconnected')
                connections.remove(c)
                c.close()
                break
            for connection in connections:
                connection.send(f'{a} said: {data.decode(unicode)}'.encode(unicode))
            print(f'Messsage from {threading.currentThread().name} {a} ==> {data.decode(unicode)}')


    while True:
        try:
            c, a = sock.accept()
            cThread = threading.Thread(target=handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            connections.append(c)
            print(f'{a[0]}:{a[1]} connected')
            time.sleep(0.05)
            print('RUNNING THREADS', file=sys.stderr)
            time.sleep(0.05)
            for thread in threading.enumerate():
                print(thread.name)
            time.sleep(0.05)
            print('---------------', file=sys.stderr)
        except KeyboardInterrupt:
            sock.close()
            print("\nConnection closed")
            break
