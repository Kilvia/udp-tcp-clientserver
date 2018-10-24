from socket_udp import create_server, recv

if __name__ == '__main__':

    host = 'localhost'
    port = 8888

    server = create_server(host, port)
    while True:
        recv(server, port)
