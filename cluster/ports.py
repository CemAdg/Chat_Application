#These module stores the port numbers used by servers for multicast, unicast etc.

MULTICAST_PORT_SERVER= 10000               #Port sending and receiving multicast messages between server
UNICAST_PORT_SERVER   = 8300               #Port used for TCP Unicast heartbeat messages between server
MULTICAST_PORT_CLIENT = 8200               #Port used for clients so send multicast message to all servers to discover leader and connect to leader

CLIENT_CONNECT_PORT_LEADERSERVER = 8080    #Port used for clients to connect to leader server and order items

SERVER_CLIENTLIST_UPDATE_PORT = 8090       #Port used for replica servers to get updated client list from leader
SERVER_SERVERLIST_UPDATE_PORT = 8060       ##Port used for replica servers to get updated server list from leader
SERVER_CHATMEMBERS_UPDATE_PORT = 8070       #Port used for replicating chat member list from leader server to member servers
SERVER_LEADER_ELECTION_PORT = 8100         #Port used for new leader election when leader crashes
SERVER_NEW_LEADER_MESSAGE_PORT = 8110      #Port used to inform all server about new leader after the election
SERVER_SEND_CHATMEMBERS_TO_NEW_LEADER_PORT= 8105  #Port used when new leader is selected after LCR it compares chat member lit with other leaders and asks for the latest one