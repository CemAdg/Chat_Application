import os
import struct
import sys
import threading
import socket
import pickle #is needed so send objects (tuple,list) through tcp
import logging
# DEBUG: Detailed information, typically of interest only when diagnosing problems.
# INFO: Confirmation that things are working as expected.
# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
# ERROR: Due to a more serious problem, the software has not been able to perform some function.

#Change Logging level to debug so we can log info in the logging file
logging.basicConfig(filename='server.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# CRITICAL: A serious error, indicating that the program itself may be unable to continue running.
from time import sleep

ROOT_DIR = os.path.dirname(os.path.abspath("")) #root path of project  --> .../OnlineShop/
sys.path.append(ROOT_DIR)    #Add path to project root otherwise imports will fail
from cluster.server_multicast import sendMulticastMessage
from cluster.ports import UNICAST_PORT_SERVER
from cluster.ports import MULTICAST_PORT_SERVER
from cluster.ports import MULTICAST_PORT_CLIENT
from cluster.ports import SERVER_CLIENTLIST_UPDATE_PORT
from cluster.ports import CLIENT_CONNECT_PORT_LEADERSERVER
from cluster.ports import SERVER_ORDERLIST_UPDATE_PORT
from cluster.ports import SERVER_LEADER_ELECTION_PORT
from cluster.ports import SERVER_NEW_LEADER_MESSAGE_PORT
from cluster.ports import SERVER_SERVERLIST_UPDATE_PORT
from cluster.ports import SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT


from cluster.lcr import *




#Constant Variables
HEADER = 64         #First message to the server tells how long message is. Represents amount of bytes of msg
FORMAT = 'utf-8'    #Format of msg

#hostname = socket.gethostname()             #Name of running machine
#host_ip_address = socket.gethostbyname(hostname) #IP adress of running machine
#host = host_ip_address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))              #connect to itself to get IP of machine. This is Necessary since sometimes server is running on 127.0.0.1 localhost
host_ip_address= s.getsockname()[0]
#port = int(sys.argv[1])  # Input port number as first argument from command line when running script


class server():
    def __init__(self):
        self.serverlist = []            #Stores the server adresses
        self.clientlist = []            #Stores the client adresses
        self.isLeader = False           #Default value

        self.heartbeatActive = False    #boolean value to track if heartbeat is running or not
        self.heartbeat_thread = threading.Thread(target=self.startHeartbeat)
        self.heartbeat_counter = 0      #Variable used for the first start of the hearbeat function
        self.servermemberUpdate = False #Evertyime serverlist is updated this value will turn into True and after the heartbeat function restarted with updated list turned back to false

        self.clientlist_vectorclock = [0,0] #First value goes up when client connects, second value goes up when client disconnects

        self.ordernumber = 0                #automatically increases by one when an order incomes
        self.orderlist = []
        self.orderlist_update_thread_started = False #turns into True if the replication of the orderlist has started

        self.leaderCrashed = False      #If leader crash is detected this value turns into True and starts the election
        #self.first_electionmsg_sent = False #Server accepts election msg only after it has sent first message


    def updateServerList(self,newserverlist):
        if len(self.serverlist)==0:  #Do nothing when serverlist is empty and finish heartbeat if all servers die and list is empty
            print('Serverlist empty heartbeat not starting')
            self.heartbeatActive=False  #End running heartbeat when no server is left in the list

            #If server already started heartbeat the counter is not 0 anymore. But when all members of the server list die
            #it's the same situation before starting heartbeat for the first time
            #set heart_counter to 0 so when again first server will be in the list the heartbeat function starts again
            self.heartbeat_counter=0

            if self.isLeader == False:
                self.isLeader=True     #This server is the only one so turn into leader server
                print("Serverlist empty. I'm the new leader")

        elif len(self.serverlist)>0:
            if self.heartbeat_counter==0:
                self.heartbeat_counter= self.heartbeat_counter +1
                self.serverlist= newserverlist         #Overwrite serverlist with updated one

                print("Starting Heartbeat first time. My serverlist:", self.serverlist)
                self.heartbeatActive=True
                self.heartbeat_thread = threading.Thread(target=self.startHeartbeat) #create new thread and run heartbeat for first time
                self.heartbeat_thread.start()
            else:
                self.serverlist = newserverlist
                print("Serverlist is updated: ", self.serverlist)
                self.servermemberUpdate= True

# **************************************************ORDERED RELIABLE MULTICAST ********************************************************

    def sendUpdatedClientList(self): #Function can only used by leader server
        if self.isLeader == True:
            if len(self.serverlist)>0:  #if server list consists at least one server replicate the updated client list to the servers
                for x in range(len(self.serverlist)):   #send new client to all replica servers in list
                    connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                    server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                    ip, port = server_adress  # split up server_adress into ip adress and port

                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
                    s.settimeout(3)# wait 3 seconds for respond

                    message1= pickle.dumps(self.clientlist_vectorclock)         #first send current vector clock and only client list when requested
                    message2 = pickle.dumps(self.clientlist) #use pickle to send objects
                    try:
                        s.connect((ip, SERVER_CLIENTLIST_UPDATE_PORT))  # Connect to Client list update port
                        s.send(message1)
                        try:
                            response = s.recv(1024)
                            response = response.decode()
                            if response=='yes': #if server requests clientlist then send it
                                s.send(message2)
                                logging.info("Client list has been sent to : {},{} ".format(ip,SERVER_CLIENTLIST_UPDATE_PORT))
                            else:
                                logging.info("Server {} already knows the client. Rejected client")
                        except socket.timeout:
                            logging.info('No response received from sent clientlist_vectorclock from:{}'.format(ip))

                    except:
                        logging.info("Failed to send clientlist to: {},{}".format(ip, SERVER_CLIENTLIST_UPDATE_PORT))
                    finally:
                        s.close()

            else:
                print("Serverlist is Empty cant replicate clientlist to member servers")

    def listenClientListUpdate(self):
        server_address = ('', SERVER_CLIENTLIST_UPDATE_PORT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()

        logging.info('Listening for clientlist updates on Port:{} '.format(SERVER_CLIENTLIST_UPDATE_PORT))

        while True:
            connection, server_address = sock.accept()  # Wait for a connection
            message1 = connection.recv(1024)              #save incoming bytes
            message1 = pickle.loads(message1)       #unpickle the message
            #print('received msg1: ',message1)
            new_clientlist_vectorclock = message1   #save the received vector clock to a variable

            #compare received vectorclock with own one. If received vectorclock is higher send request for clientlist
            if new_clientlist_vectorclock[0]> self.clientlist_vectorclock[0] or new_clientlist_vectorclock[1]> self.clientlist_vectorclock[1] :
                logging.info('New client list vector_clock {}, my clientlist vector_clock {}'.format(new_clientlist_vectorclock,self.clientlist_vectorclock))
                logging.info("Send request for updated client list")

                response = 'yes'
                response = response.encode()
                connection.send(response)

                message2 = connection.recv(1024)
                message2 = pickle.loads(message2)
                self.clientlist = message2  # overwrite old list with received updated list
                self.clientlist_vectorclock = new_clientlist_vectorclock #update vectorclock
                print('Received update from leader. My clientlist: ', self.clientlist)
                logging.info('Received update from leader. My clientlist: {} '.format(self.clientlist))
            else:
                response = 'no'
                response = response.encode()
                connection.send(response)
                print('Rejected client list update. My clientlist_vectorclock:',self.clientlist_vectorclock,'Leader clientlist_vectorclock:',new_clientlist_vectorclock)


#**************************************************HEARTBEAT ********************************************************

    def restartHeartbeat(self):
        if self.servermemberUpdate==True:
            self.servermemberUpdate = False #latest update received

            if self.leaderCrashed==True:    #if leader crashed start election
                self.leaderCrashed=False
                print('Starting Leader Election')
                startElection(self.serverlist,host_ip_address)

            print("Restarting Heartbeat")
            self.heartbeat_thread = threading.Thread(target=self.startHeartbeat)  #overwrite dead thread and create new thread and rerun heartbeat
            self.heartbeatActive = True
            self.heartbeat_thread.start()

    def startHeartbeat(self):
        message = ('Heartbeat')
        failed_server= -1       #inital value -1 means there is no failed server at the moment

        while self.heartbeatActive:
            sleep(3)#failure detection every 3 seconds
            for x in range(len(self.serverlist)):
                if self.servermemberUpdate==True:
                    self.heartbeatActive=False
                    break
                connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                ip, port = server_adress  # split up server_adress into ip adress and port

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
                s.settimeout(2)  # set timeout for every socket to 1 seconds
                try:
                    s.connect((ip, UNICAST_PORT_SERVER))  # Connect each socket to ip adress and UNICAST Port
                    s.send(message.encode())
                    logging.info("Sending Heartbeat: Heartbeatmsg sent to: {},{} ".format(ip,UNICAST_PORT_SERVER))
                    try:
                        response = s.recv(1024)
                        logging.info("Sending Heartbeat: Received Heartbeat response: {}".format(response.decode()))
                    except socket.timeout:
                        logging.info('Sending Heartbeat: No responto to heartbeat from: {} '.format(ip))



                        # if no response is received remove server from list
                except:
                    logging.info("Sending Heartbeat: Server not online can't connect to: {},{} ".format(ip, UNICAST_PORT_SERVER))
                    failed_server = x   #Position of failed server in the server list

                    if isLeader == True:            #Crashed server is the leader
                        self.leaderCrashed= True
                        logging.info('Leader crash detected'.format(server_adress,isLeader))
                        #print ('Leader crashed')

                finally:
                    s.close()

            if failed_server>=0:    #If a failed server is detected
                newserverlist = self.serverlist
                del newserverlist[failed_server]
                if self.leaderCrashed==True:
                    print('Removed crashed leader server',ip,'from serverlist')
                else:
                    print('Removed crashed server', ip, 'from serverlist')

                self.updateServerList(newserverlist)
                self.heartbeatActive=False

            #check if heartbeatActive value has changed
            if  self.heartbeatActive==False:    #everytime serverlist is updated self.heartbeatActive will set to False to end thread
                break

        print('Stopped Heartbeat!')
        self.restartHeartbeat()

    def listenHeartbeat(self):  #create socket and bind socket to unicast port and listen for heartbeat messages
        server_address = ('', UNICAST_PORT_SERVER)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Listening to Heartbeat on Port: {} '.format(UNICAST_PORT_SERVER))
        while True:
            connection, server_address = sock.accept() # Wait for a connection
            heartbeat_msg = connection.recv(1024)
            heartbeat_msg = heartbeat_msg.decode()
            logging.info ('Listening Heartbeat: received Heartbeat from: {} '.format(server_address))
            if heartbeat_msg:
                logging.info('Listening Heartbeat: sending Heartbeat back to: {} '.format(server_address))
                connection.sendall(heartbeat_msg.encode()) #sendall sends the entire buffer you pass until everything has been sent or an error occurs

# **************************************************ORDERED RELIABLE MULTICAST ********************************************************

    def sendOrderlistUpdate(self):

        while True:
            if len(self.serverlist) ==0 :
                print('No replica servers in the list. Not asking for orderlist updates')

            if len(self.serverlist) >0 :    #only update when the are member servers
                print('Asking replica servers for orderlist update')
                for x in range(len(self.serverlist)):   #Iterate through serverlist
                    connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                    server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                    ip, port = server_adress  # split up server_adress into ip adress and port

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
                    s.settimeout(2)  # set timeout for every socket to 1 seconds
                    try:
                        s.connect((ip, SERVER_ORDERLIST_UPDATE_PORT))  # Connect to each member servers SERVER_ORDERLIST_UPDATE_PORT
                        ordernumber = pickle.dumps(self.ordernumber)
                        s.send(ordernumber)                          #send ordernumber and wait for the response

                        response = s.recv(1024)
                        response = pickle.loads(response)
                        logging.info('Server: {} send his ordernumber {}. My ordernumber is: {}'.format(ip,response, self.ordernumber))
                        if response =='no':                 #Member send 'no' as msg which means it doesnt need update
                            logging.info('No Update needed for server: '.format(ip))                            #Do nothing continue with for loop and ask next member server
                        else:
                            for i in range(self.ordernumber-response):  #difference between leader order number and received replica server ordernumber
                                if i == 0:  # only for the first round of the loop
                                    # response==0 means member has no orderlist. So we have to start from the first element in orderlist which is orderlist[0]
                                    if response == 0:
                                        missing_element = 1
                                    else:  # if response is not 0. We need the next element of response. e.g leader element 10, response 7 means we need the 8. 9. and 10. element of the order list
                                        missing_element = response + 1

                                missing_order= pickle.dumps(self.orderlist[missing_element-1])  #List index begins with zero therefore subtract -1 to get missing element
                                s.send(missing_order)
                                logging.info('Updating server: Sending ordernumber: {} to server {}'.format(response+i+1,ip))
                                ack_missing_order = s.recv(1024)
                                ack_missing_order= ack_missing_order.decode()
                                logging.info('Updating server: Received ack msg:{} , for ordernumber {} from server {} '.format(ack_missing_order,response+i+1,ip))
                                missing_element += 1  # count up to get the next needed element in orderlist
                    except:
                        print('Could not connect or send msg to:', ip,',',SERVER_ORDERLIST_UPDATE_PORT)
                        pass
                    finally:
                        s.close()
            sleep(30)   #Updates will be sent every 30 secs

    def listenforOrderlistUpdate(self):
        server_address = ('', SERVER_ORDERLIST_UPDATE_PORT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Listening to Orderlist Updates on Port: {} '.format(SERVER_ORDERLIST_UPDATE_PORT))
        while True:
            connection, server_address = sock.accept()  # Wait for a connection
            leader_ordernumber = connection.recv(1024)
            leader_ordernumber = pickle.loads(leader_ordernumber)   #unpickle the order number and compare to own


            if leader_ordernumber > self.ordernumber:   #The leader has more orders in his list than this server so ask for the missing orders
                own_ordernumber= pickle.dumps(self.ordernumber)     #send own ordernumber back so leader can send missing orders
                connection.send(own_ordernumber)
                for i in range(leader_ordernumber-self.ordernumber):
                    missing_order = connection.recv(1024)           #wait for missing order
                    missing_order = pickle.loads(missing_order)
                    ack_msg_missing_order = 'Received missing order'
                    connection.send(ack_msg_missing_order.encode())
                    self.orderlist.append(missing_order)            #add missing order in own list
                    self.ordernumber +=1                            #count up own ordernumber
                    logging.info('Added missing order {} to my orderlist'.format(missing_order))
                print('Received missing updates from leader server. Current orderlist: ', self.orderlist)
            else:
                msg = 'no'              #Server dont need update
                msg = pickle.dumps(msg)
                connection.send(msg)
                print('No updates received. Orderlist already equal to leader orderlist ')

# ************************************************* NEW LEADER ELECTION ****************************************************

    def sendnewLeaderMessage(self):
        if self.isLeader==True:
            message = host_ip_address      #IP of new leader

            for x in range(len(self.serverlist)):
                connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                ip, port = server_adress  # split up server_adress into ip adress and port

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
                s.settimeout(2)  # set timeout for every socket to 1 seconds
                try:
                    s.connect((ip, SERVER_NEW_LEADER_MESSAGE_PORT))  # Connect to every servers socke to inform about new leader
                    s.send(message.encode())
                    logging.info("Sent newLeaderMessage to: {},{} ".format(ip, SERVER_NEW_LEADER_MESSAGE_PORT))
                    print('Sending newLeaderMessage to ',ip )
                    try:
                        response = s.recv(1024)
                        logging.info("Received ack from sent newLeaderMessage from: {}".format(ip,response.decode()))
                    except socket.timeout:
                        pass
                finally:
                    s.close()           #Close socket

    def listenforNewLeaderMessage(self):
        server_address = ('', SERVER_NEW_LEADER_MESSAGE_PORT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Listening to NewLeaderMessage on Port: {} '.format(SERVER_NEW_LEADER_MESSAGE_PORT))
        while True:
            connection, server_address = sock.accept()  # Wait for a connection
            newleader_ip = connection.recv(1024)
            newleader_ip = newleader_ip.decode()

            for i in range(len(self.serverlist)):   #search for the leader IP in the serverlist
                connection_and_leader = self.serverlist[i]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                ip, port = server_adress  # split up server_adress into ip adress and port
                if ip == newleader_ip:  #When ip in list matches the leader ip change the isLeader value to True
                    self.serverlist[i]=server_adress,True   #Overwrite old value with new value. Same adress but True for new leader


            response = 'ack msg.Received new leader information'    #send back ack msg
            connection.send(response.encode())

            logging.info('Received newLeaderMessage. New leader is:'.format(newleader_ip,isLeader))
            print('Received newLeaderMessage: new leader is:',newleader_ip)
            print('Updated my serverlist: ',self.serverlist)


    def listenforElectionMessage(self):
        server_address = ('', SERVER_LEADER_ELECTION_PORT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Listening for LCR Election messages on Port: {} '.format(SERVER_LEADER_ELECTION_PORT))
        while True:
            connection, server_address = sock.accept()  # Wait for a connection
            received_ip = connection.recv(1024)
            received_ip = received_ip.decode()         #Otherwise it is a IP and election is still running
            sleep(2)
            logging.info('Listening LCR Election messages: received election message: {} from {} '.format(received_ip,server_address))



            if socket.inet_aton(received_ip) == socket.inet_aton(host_ip_address):          #If I received my IP. I am the leader
                print("Leader Election: I'm the new leader")
                self.isLeader=True
                self.sendnewLeaderMessage()             #Inform other servers about the new leader

                print('Checking for orderlist updates on member servers')

                self.getLatestOrderlistfromServer()

                if len(self.clientlist)>0:
                    print('Checking for orderlist updates on clients')
                    self.getLatestOrderlistfromClient()

                if self.ordernumber>0:
                    print('Restarting orderlist update thread')
                    thread = threading.Thread(target=self.sendOrderlistUpdate)
                    thread.start()

            elif socket.inet_aton(received_ip) > socket.inet_aton(host_ip_address):  # e.g 192.168.0.67 > 192.168.0.55, if received IP is higher pass on to neighbor
                print('Received IP(',received_ip ,') is higher than own(',host_ip_address,'). Passing higher IP to neighbour')
                sendElectionmessage(received_ip)
            else:
                print('Received IP(',received_ip ,') is lower than own(',host_ip_address,') Not passing to my neighbour')


    def listenforNewLeaderOrderlistRequest(self):
        server_address = ('', SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Waiting for new Leader to request Orderlist on Port: {} '.format(SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT))
        while True:
            connection, server_address = sock.accept()  # Wait for a connection
            leader_ordernumber = connection.recv(1024)
            leader_ordernumber = pickle.loads(leader_ordernumber)
            print('Received ordernumber from leader:',leader_ordernumber)

            if self.ordernumber == leader_ordernumber or self.ordernumber < leader_ordernumber:
                print('Ordernumber identical with leader server')
                response='no'       #there are no updates
                connection.send(response.encode())
            else:
                print('My ordernumer is higher than leader order number. Sending order updates')
                message = pickle.dumps(self.orderlist)
                connection.send(message)


    def getLatestOrderlistfromServer(self):
        for x in range(len(self.serverlist)):
            connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
            server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
            ip, port = server_adress  # split up server_adress into ip adress and port

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
            s.settimeout(2)  # set timeout for every socket to 1 seconds

            try:
                s.connect((ip, SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT))  # Connect to each member server
                ordernumber = pickle.dumps(self.ordernumber)
                s.send(ordernumber)  # send ordernumber and wait for the response

                response = s.recv(1024)
                try:
                    response = pickle.loads(response)
                except:
                    response = response.decode()

                if response == 'no':
                    logging.info('New Leader: Orderlist of leader server and server {} is identical '.format(ip))  # Do nothing continue with for loop and ask next member server
                    print('New Leader: Orderlist of leader server and server',ip, ' is identical')
                else:
                    self.orderlist = response
                    self.ordernumber = len(self.orderlist)
                    print('Restored latest list form server', ip)
                    print('Current orderlist:', self.orderlist, 'Current ordernumber:',self.ordernumber)

            except:
                print('Could not connect or send msg to:', ip, ',', SERVER_SEND_ORDERLIST_TO_NEW_LEADER_PORT)
            finally:
                s.close()


    def getLatestOrderlistfromClient(self):
        for x in range(len(self.clientlist)):
            client_ip,client_port = self.clientlist[x]
            client_order_request_port = client_port +200    #this is the port where every client is listening for requests for missed orders

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
            s.settimeout(2)  # set timeout for every socket to 1 seconds

            leader_ordernumber_msg = pickle.dumps(self.ordernumber)

            try:
                s.connect((client_ip, client_order_request_port))  # Connect to every servers socke to inform about new leader
                s.send(leader_ordernumber_msg)

                response = s.recv(1024)
                try:                                #if the client has no higher orderid response will be 'no' which is string
                    response = response.decode()
                    print('Client',self.clientlist[x],'has no missed orders')
                except:                             #if response can not be decoded it means it's no string. It will be list of missed orders
                    missed_order_list=[]
                    missed_order_list = pickle.loads(response)

                    for i in range(len(missed_order_list)):
                        self.orderlist.append(missed_order_list[i])
                        self.ordernumber +=1

                    print('Client',self.clientlist[x],'has sent', len(missed_order_list),'missed orders')
                    self.orderlist.sort(key=lambda x: x[0])  # after adding missed orders. Sort orderlist


            except:
                pass    #if connection cant be establish client is offline
        print('Latest orderlist:', self.orderlist)

# ************************************************* CLIENT SOCKET ****************************************************

    def listenforOrders(self,conn,addr):
        while True:
            sleep(2)
            ordermsg = conn.recv(1024)
            ordermsg = ordermsg.decode()


            #If clients disconnects end while loop


            if ordermsg == 'disconnect' or len(ordermsg) == 0:  # on Keyboard Interupt (CTRL-C) client will send "disconnect" when closind scirpt socket send 0 bytes
                for i in range(len(self.clientlist)):
                    if addr == self.clientlist[i]:
                        print('Client', addr, "has disconnected")
                        del self.clientlist[i]
                        self.clientlist_vectorclock[1] +=1
                        logging.info('Client removed and client list updated:{}'.format(self.clientlist))
                        self.sendUpdatedClientList()

                    break
            else:
                print('Received order from:',addr, ordermsg)
                self.ordernumber +=1                        #increase ordernumber by one
                self.orderlist.append((self.ordernumber,addr,ordermsg)) #save tuple of ordernumber,addr, ordermsg in a list

                if self.ordernumber == 1: #Start updating thread when the first order is received
                    print('First order received starting updating thread')
                    thread = threading.Thread(target=self.sendOrderlistUpdate)
                    thread.start()

                print('Total orderlist:',self.orderlist)
                orderconfirm = ((self.ordernumber,addr,ordermsg))
                orderconfirm = pickle.dumps(orderconfirm)
                conn.sendall(orderconfirm)

    def listenforConnections(self,s):
        while True:  # Waiting forever for connections, everytime a new connection occures create a thread
            if self.isLeader==True: #only acccept client connection when the server is the leader server
                conn, addr = s.accept()  # Accept incoming connections

                if self.clientlist: #check if it's a new connection when a clientlist already exists
                    for i in range(len(self.clientlist)):
                        if addr == self.clientlist[i]:
                            client_already_in_list = True
                            break
                        else:
                            client_already_in_list = False

                    if client_already_in_list == False:
                        print("Client ", addr, " has connected to the server and is now online ...")
                        self.clientlist.append(addr)  # Save incoming connection in List
                        self.clientlist_vectorclock[0] += 1  # everytime a client connects first element increases by 1
                        print("Updated client list: ", self.clientlist)
                        self.sendUpdatedClientList()  # send updated client list to all replica servers


                        # Create new thread for every connected client. Each thread handles order from one client.
                        thread = threading.Thread(target=self.listenforOrders, args=(
                        conn, addr))  # conn is socket from client, s is socket from server
                        thread.start()
                    else:
                        print("Client ", addr, " has reconnected to the server and is now online ...")
                        self.sendUpdatedClientList()  # send updated client list to all replica servers
                        thread = threading.Thread(target=self.listenforOrders, args=(
                        conn, addr))  # conn is socket from client, s is socket from server
                        thread.start()

                else:
                    self.clientlist.append(addr)  # Save incoming connection in List
                    self.clientlist_vectorclock[0] +=1  #everytime a client connects first element increases by 1
                    print("Client ", addr, " has connected to the server and is now online ...")
                    print("Updated client list: ", self.clientlist)
                    self.sendUpdatedClientList()    #send updated client list to all replica servers


                    #Create new thread for every connected client. Each thread handles order from one client.
                    thread = threading.Thread(target=self.listenforOrders, args=(conn,addr))   #conn is socket from client, s is socket from server
                    thread.start()

    def listenClientMulticast(self):        #Listen for Client multicast messages and response with isLeaderValue
        #this function is for clients to discover the leader server and connect to leader server
        multicast_group = '224.3.29.71'
        server_address = ('', MULTICAST_PORT_CLIENT)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create the socket
        sock.bind(server_address)  # Bind to the server address

        # Tell the operating system to add the socket to the multicast group on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Receive/respond loop
        logging.info('Listen to Client Multicast Address: {} {}'.format(multicast_group,MULTICAST_PORT_CLIENT))
        while True:
            data, address = sock.recvfrom(128)
            logging.info('Listen Client multicast: received {} bytes from {}'.format (len(data), address))
            logging.info('Listen Client multicast: sending isLeader Value: {} to {}'.format(self.isLeader,address))

            if self.isLeader:           #If isLeader is True Leader Server responds with "True"
                msg_ack = 'True'
            else:
                msg_ack = 'False'
            sock.sendto(msg_ack.encode(), address)


    def sendUpdatedServerList(self):
        if self.isLeader == True:
            if len(self.serverlist) > 0:  # if server list consists at least one server replicate the updated client list to the servers
                for x in range(len(self.serverlist)):  # send new client to all replica servers in list
                    connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                    server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                    ip, port = server_adress  # split up server_adress into ip adress and port

                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # create one heartbeat TCP socket for each server
                    s.settimeout(3)  # wait 3 seconds for respond

                    try:
                        s.connect((ip, SERVER_SERVERLIST_UPDATE_PORT))  # Connect to Client list update port

                        updatedserverlist = pickle.dumps(self.serverlist)
                        s.send(updatedserverlist)
                        try:
                            response = s.recv(1024)
                            response = response.decode()
                            logging.info("Updated serverlist has been sent to : {} ".format(ip))
                        except socket.timeout:
                            logging.info('No response received from sent serverlist from:{}'.format(ip))

                    except:
                        logging.info("Failed to send serverlist to: {}".format(ip))
                    finally:
                        s.close()
            else:
                print("Serverlist is Empty cant replicate serverlist to member servers")

    def listenServerListUpdate(self):
        server_address = ('', SERVER_SERVERLIST_UPDATE_PORT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP/IP socket
        sock.bind(server_address)  # Bind to the server address
        sock.listen()
        logging.info('Listening for serverlist updates on Port:{} '.format(SERVER_SERVERLIST_UPDATE_PORT))

        while True:
            connection, leader_address = sock.accept()  # Wait for a connection

            leaderserverlist = connection.recv(2048)              #save incoming bytes
            leaderserverlist = pickle.loads(leaderserverlist)       #unpickle the message

            newserverlist = []                                #create new list
            newserverlist = leaderserverlist                  #store leaderserverlist in new list

            serverlist_lenght = len(newserverlist)          #store lenght of newserverlist in variable. Since the list will be modified

            for x in range(serverlist_lenght):
                connection_and_leader = newserverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables
                ip, port = server_adress  # split up server_adress into ip adress and port
                if ip == host_ip_address:   #remove own ip from list
                    del newserverlist[x]
                    newserverlist.append((leader_address,True))    #add leader server to list
                    self.serverlist=newserverlist                 #Overwrite own list with new one
                    sleep(0.5)                                    #just to print Receveived Multicast msg from leader before starting heartbeat message
                    self.updateServerList(self.serverlist)          # Overwrite old serverlist with updated one


#************************************************** MULTICAST ********************************************************

    def listenMulticast(self):
        multicast_group = '224.3.29.71'
        server_address = ('', MULTICAST_PORT_SERVER)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   # Create the socket
        sock.bind(server_address) # Bind to the server address

        # Tell the operating system to add the socket to the multicast group on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Receive/respond loop
        logging.info('Listen to Multicast Address {} {}:'.format(multicast_group,MULTICAST_PORT_SERVER))
        while True:
            data, address = sock.recvfrom(128)
            logging.info('Listen multicast: received {} bytes from {}'.format(len(data), address))
            logging.info('Listen multicast: sending acknowledgement to {}'.format(address))

            if self.isLeader:           #If isLeader is True Leader Server responds with "True"
                msg_ack = 'True'
            else:
                msg_ack = 'False'

            sock.sendto(msg_ack.encode(), address)

            if self.isLeader==True:
                if len(self.serverlist)==0:         #If there is no server in the list add and send update
                    self.serverlist.append((address, False))  # Add new connection
                    self.updateServerList(self.serverlist)  # Overwrite serverlist with updated one
                    self.sendUpdatedServerList()  # Send updated list to all servers
                else:
                    # check if the connection is already in the list
                    for x in range(len(self.serverlist)):
                        connection_and_leader = self.serverlist[x]  # serverlist consists a tuple of a tuple and a boolean. The inside tuple are the connection details host ip and port
                        replica_server_adress, isLeader = connection_and_leader  # split up tuple into sinlge variables

                        if  replica_server_adress == address:  #Check if connection is already in list when yes dont add it
                            break
                        else:
                            self.serverlist.append((address,False))   #Add new connection
                            self.updateServerList(self.serverlist)  # Overwrite serverlist with updated one
                            self.sendUpdatedServerList()            #Send updated list to all servers
                            break




            if len(self.clientlist)>0:      #When a new server is online and a client list exists update new server with client list
                self.sendUpdatedClientList()

    def startMulticastMessage(self):
        sendMulticastMessage() #start discovering leader server


#************************************************* CLIENT SOCKET ****************************************************
    def startServer(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #SOCK_STREAM means that it is a TCP socket
            #host = socket.gethostbyname(socket.gethostname())      #get IP from running machine , Gibt manchmal 127.0.0.1 aus statt 192. ...
            logging.info("Server started on host and port {}, {} : ".format(host_ip_address,CLIENT_CONNECT_PORT_LEADERSERVER))
            print("Server started on host : ", host_ip_address)
            s.bind((host_ip_address,CLIENT_CONNECT_PORT_LEADERSERVER))                                     #Bind to the port

            #Calling listen() puts the socket into server mode
            s.listen()                                              #Listen/wait for new connections
            logging.info("Server is waiting for incoming client connections...")
            #print("Server is waiting for incoming client connections...")

            # Create new thread and wait for new connections to occure
            thread = threading.Thread(target=self.listenforConnections, args=(s,))
            thread.start()
        except socket.error as msg:
            print('Could Not Start Server Thread. Error Code : ')  # + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()


if __name__ == '__main__':
    s = server() #create new server

    try:
        first_argv = sys.argv[1]
        if first_argv == 'leader' or 'Leader':
            print('Starting as leader server:')
            s.isLeader=True
    except:
        pass


    s.startServer()

    if s.isLeader == False:
        thread1 = threading.Thread(target=s.listenServerListUpdate) #only listen for serverlist updates if server is not leader server
        thread1.start()
        s.startMulticastMessage() #discover leader server

        thread2 = threading.Thread(target=s.listenforNewLeaderOrderlistRequest)
        thread2.start()


    thread3 = threading.Thread(target=s.listenClientListUpdate)
    thread3.start()

    thread4 = threading.Thread(target=s.listenHeartbeat)
    thread4.start()

    thread5 = threading.Thread(target=s.listenforNewLeaderMessage)
    thread5.start()

    thread6= threading.Thread(target=s.listenforElectionMessage)
    thread6.start()

    thread7 = threading.Thread(target=s.listenMulticast)
    thread7.start()

    thread8 = threading.Thread(target=s.listenClientMulticast)
    thread8.start()

    thread9 = threading.Thread(target=s.listenforOrderlistUpdate)
    thread9.start()
