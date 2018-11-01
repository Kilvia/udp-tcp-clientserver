from threading import Thread, Condition
from time import time
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
        global packages_time
        packages_time = []
      
        aux = 0
        j = 0

        for i in range(0, 7):
            # Cria uma janela de tamanho 7
            t_window.append((None,None))

        initial_time = time()      
       
        send_thread = Thread(target = send, args = (client, host, port, t_window, lock_w))
        recv_ack_thread = Thread(target = recv_ack, args = (client, host, port, t_window, lock_w, lasted_ack, packages_time))
        
        send_thread.start()
        recv_ack_thread.start()
        
        send_thread.join()
        recv_ack_thread.join()

        final_time = time()
        total = final_time - initial_time
        print(packages_time)
        
        for i in packages_time:
            aux += i
            j += 1
        
        print(j)
        aux = aux/j

        print("\n******************************************************")
        print("************** \t\tTempo Total  *****************")
        print("****  \t\t{}s\t\t  ****".format(total))
        print("******************************************************")
        print("****  \t\tAtraso Médio dos Pacotes\t  ****")
        print("****  \t\t{}s\t\t  ****".format(aux))
        print("******************************************************")
    
    except:
        print ("Error: unable to start thread")