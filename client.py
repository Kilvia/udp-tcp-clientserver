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

        # Inicia o tempo de execução do cliente
        initial_time = time()      
       
        send_thread = Thread(target = send, args = (client, host, port, t_window, lock_w))
        recv_ack_thread = Thread(target = recv_ack, args = (client, host, port, t_window, lock_w, lasted_ack, packages_time))
        
        send_thread.start()
        recv_ack_thread.start()
        
        send_thread.join()
        recv_ack_thread.join()

        # Finaliza o tempo de execução do cliente
        final_time = time() 

        # Calcula o tempo de execução do cliente
        total = final_time - initial_time
        
        # Soma o todos os tempos armazenados e a quantidade de elementos armazenados
        for i in packages_time:
            aux += i
            j += 1

        # Média de atrasos
        aux = aux/j

        print("\n******************************************************")
        print("****\t\tTempo de Envio dos Dados\t  ****")
        print("****  \t\t\t{}s\t\t\t  ****".format(round(total, 3)))
        print("******************************************************")
        print("****\t\tAtraso Médio dos Pacotes\t  ****")
        print("****  \t\t\t{}s\t\t\t  ****".format(round(aux, 3)))
        print("******************************************************")
    
    except:
        print ("Error: unable to start thread")