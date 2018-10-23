import threading
from socket_udp import *

if __name__ == '__main__':
  
    #host = '192.168.1.30'          #home
    host = 'localhost'             #larces
    port = 8888

    client = create_client(host, port)
    try:
        send_thread = threading.Thread(target = send, args = (client, '', port, host))
        recv_ack_thread = threading.Thread(target = recv_ack, args = (client, '', port, host))
        send_thread.start()
        recv_ack_thread.start()
        # _thread.start_new_thread( send, (client, '', port, host) )
        #_thread.start_new_thread( recv_ack, (client, '', port, host) )
    except:
        print ("Error: unable to start thread")