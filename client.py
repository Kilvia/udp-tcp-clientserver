from threading import Thread, Condition
from socket_udp import *

if __name__ == '__main__':
  
    #host = '192.168.1.30'          #home
    host = 'localhost'             #larces
    port = 8888

    client = create_client(port)
    
    try:
        global t_window
        t_window = []
        global lasted_ack, max_packages
        lasted_ack = 0
        max_packages = 2
        global lock_w
        lock_w = Condition()
        for i in range(0, 7):
            t_window.append((None,None))
        send_thread = Thread(target = send, args = (client, host, port, t_window, lock_w, max_packages))
        recv_ack_thread = Thread(target = recv_ack, args = (client,  t_window, lock_w, lasted_ack, max_packages))
        send_thread.start()
        recv_ack_thread.start()

    except:
        print ("Error: unable to start thread")