from server import hAddress as s_1
from server_2 import hAddress as s_2
from server_3 import hAddress as s_3

server_list = [s_1, s_2, s_3]

print(server_list)

text = ''

while True:
    activeServer = input()

    if activeServer == '2':
        for x in server_list:
            print(x)