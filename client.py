from socket_udp import *

if __name__ == '__main__':
  
    #host = '192.168.1.30'          #home
    host = 'localhost'             #larces
    port = 8888

    client = create_client(host, port)
    while True:
        data = input("Enter message to send : ")
        send(client, '', port, data, host)
