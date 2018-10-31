from threading import Thread, Condition
from socket_udp import *

if __name__ == '__main__':
  
    host = 'localhost'            
    port = 8888

    client = create_client(port)
    
    try:
        # Variaveis compartilhadas 
        global t_window
        t_window = []
        global lasted_ack
        lasted_ack = 0
        global lock_w
        lock_w = Condition()
      
        for i in range(0, 7):
            # Cria uma janela de tamanho 7
            t_window.append((None,None))
        
        send_thread = Thread(target = send, args = (client, host, port, t_window, lock_w))
        recv_ack_thread = Thread(target = recv_ack, args = (client, host, port, t_window, lock_w, lasted_ack))
        send_thread.start()
        recv_ack_thread.start()

    except:
        print ("Error: unable to start thread")