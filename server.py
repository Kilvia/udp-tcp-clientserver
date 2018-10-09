from socket_udp import *

if __name__ == '__main__':

    host = 'localhost'
    port = 8888

    server = create_server(host, port)
    recv(server, port)
