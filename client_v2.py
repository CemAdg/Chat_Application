import os
import pickle
import socket
import struct
import sys
import threading
from time import sleep
ROOT_DIR = os.path.dirname(os.path.abspath("")) #root path of project  --> .../OnlineShop/
sys.path.append(ROOT_DIR)    #Add path to project root otherwise imports will fail


from cluster.ports import MULTICAST_PORT_CLIENT



HEADER = 64 #First message to the server tells how long message is. Represents amount of bytes of msg
FORMAT = 'utf-8'

port = 8080 #Server Port

#Input IP Adress of Server
#host = input("Please enter the hostname of the server : ")




class client():
    def __init__(self):
        self.leader_server_found = False    #stops multicasting when leader server is found
        self.client_orderlist = []                 #stores placed orders in list

        self.client_socket = ''

        self.invalidorder = True            #Checks if orders are placed correctly
        self.connectedToLeader = False      #Checks if leader server is still online
        self.order_port = 0               #This is port of the client where connection to the leader establishes. When running client user has to input a port
        self.leader_order_request_port = 0  #New Leader uses this port to get missed orders from client and restore order history

    def discoverLeaderServer(self):
        message = ('Client Multicast Message')
        #multicast_group = ('224.3.29.71', MULTICAST_PORT_CLIENT)
        multicast_group = ('224.0.0.1', MULTICAST_PORT_CLIENT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)       # Create the datagram socket
        sock.settimeout(2)    # Set a timeout so the socket does not block indefinitely when trying # to receive data. (in sec flaot)
        ttl = struct.pack('b', 1)         # Set the time-to-live for messages to 1 so they do not go past the local network segment.
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        while(not self.leader_server_found):
            try:
                # Send data to the multicast group
                print('Client Multicast message sending "%s"' % message)
                sent = sock.sendto(message.encode(), multicast_group)

                # Look for responses from all recipients
                while True:
                    print('Client Multicast: Waiting to receive respond to sent multicast message')
                    try:
                        data, server_addr = sock.recvfrom(1024)  # receive 128 bytes at once

                        if data.decode() == "True":
                            leader_server, port = server_addr  # split up server_adress into ip adress and port
                            self.leader_server_found = True    #Leader Server discovered stop multicasting

                    except socket.timeout:
                        print('Timed out, no more responses')
                        break
                    else:
                        print('received "%s" from %s' % (data.decode(), server_addr))

            except KeyboardInterrupt:   #on CTRL-C
                break
            except:
                print("Failed to send multicast message")


        sock.close()

        self.connectToLeaderServer(leader_server)

    def connectToLeaderServer(self,leader_server):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind(('',self.order_port))      #Connection port for the client


        self.client_socket.connect((leader_server, port))
        print("Client connected to Leader Server: ", leader_server)
        self.connectedToLeader = True
        print("Welcome to the Online Shop! Choose from list below and place your order:\n \n Laptop \n Smartphone \n Tablet \n \n Please use the following format (article name,amount) Example: Laptop,5 \n"
              "Enter 'disconnect' to close the client connection")
        while self.connectedToLeader:

            while self.invalidorder :                       #Check valid input
                order_msg = input(">>Type your order: ")
                try:
                    article, amount = order_msg.split(',')
                    int(amount)
                    if  article == 'Laptop' or  article == 'Smartphone' or article == 'Tablet':
                        self.invalidorder=False
                    else:
                        print('Invalid input. Retry')
                except:
                    if order_msg == 'disconnect':
                        print('Disconnecting Client')
                        self.invalidorder = False
                    else:
                        print("Invalid input. Retry")


            #After a valid input the order msg can be sent
            self.invalidorder=True            #Change value to True so next order can checked before send

            #try except einbauen falls connection nicht klappt break
            try:
                print('Trying to send order')
                self.client_socket.send(order_msg.encode()) #send order
            except:
                print('Order could not be sent')
                self.connectedToLeader = False #leader crashed
                break

            response = self.client_socket.recv(1024)         #wait for order confirmation

            if len(response)==0:    #0 bytes means leader crashed
                print("Leader Server not online, starting leader discovery again")
                self.connectedToLeader = False
            else:
                response = pickle.loads(response)
                self.client_orderlist.append(response)
                print('Received order confirmation', response)
                #print('My total orderlist:', self.client_orderlist)


        self.client_socket.close()       #Close the client socket and start discovery again for leader server

        self.leader_server_found=False #since we have no leader set value back to inital
        self.discoverLeaderServer()

    def disconnectToLeaderServer(self):
        msg = 'disconnect'
        msg = msg.encode()
        self.client_socket.send(msg)

        self.client_socket.close()

    def listenforLeaderOrderRequest(self):
        server_address = ('', self.leader_order_request_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()

        while True:
            missed_order_list = []      #create everytime empty list

            connection, server_address = sock.accept()  # Wait for a connection
            received_ordernumber = connection.recv(1024)

            received_ordernumber = pickle.loads(received_ordernumber)   #unpickle ordernumebr from leader

            if len(self.client_orderlist)==0: #no orders send no to leader server
                response = 'no'
                connection.send(response.encode())
            else:                   #look in orderlist if there is a order id higher than leader order id
                for x in range(len(self.client_orderlist)):
                    id, myconnection, order = self.client_orderlist[x]
                    if id > received_ordernumber:
                        missed_order_list.append(self.client_orderlist[x])  #id is higher put in to list
                    else:
                        pass    #do nothing
                if len(missed_order_list)>0 :       #send missed orders to server
                    response = pickle.dumps(missed_order_list)
                    connection.send(response)
                else:               #client has no missed orders to send
                    response = 'no'
                    connection.send(response.encode())



if __name__ == '__main__':
    try:
        c = client()

        valid_input=False
        while not valid_input:
            c.order_port = int(input(">>Type in port number between 9000-9100: "))
            if c.order_port>=9000 and c.order_port <= 9100:
                c.leader_order_request_port = c.order_port+200
                valid_input=True
            else:
                print('Invalid port number. Try again')

        thread = threading.Thread(target=c.listenforLeaderOrderRequest)
        thread.start()

        c.discoverLeaderServer()    #Look for Leader Server and connect

    except KeyboardInterrupt:
        print(' Disconnecting client')
        c.disconnectToLeaderServer()
