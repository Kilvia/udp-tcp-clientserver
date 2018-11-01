import socket
import sys
from time import sleep, time
from p_client import *
from p_server import *
import pickle
import random
from threading import Condition

# Funções para criar os sockets

# Cria um socket servidor
def create_server(host, port):
   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        print("Failed to create socket. " + error)
        sys.exit()

    try:
        s.bind((host, port))
    except socket.error as error:
        print("Bind failed. Error Code :", error)
        sys.exit()

    print("Socket bind complete")

    return s

# Cria um socket cliente
def create_client(port):
   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        print("Failed to create socket. " + error)
        sys.exit()
    
    return s

# Funções do Servidor

# Função para receber os pacotes
def recv(s):
  
    # Ultimo ack recebido
    last_ack = -1
   
    while(1):
        # Recebe o pacote e o endereço do cliente
        data, add = s.recvfrom(4096)
        packet = pickle.loads(data)

        probability = random.randint(1,10)
        
        # Utiliza uma probalidade de 30% para que o pacote demore mais para responder
        if(probability < 4):
            sleep(random.uniform(0.8, 1.8))
        
        # Utiliza uma probalidade de 60% para que o pacote responda no tempo certo
        elif(probability < 10):
            last_ack = send_confirm(s, packet, add, last_ack)
       
        # Utiliza uma probalidade de 10% para que o pacote se perca e não responda


# Função para enviar um ack para o cliente
def send_confirm(s, packet, add, last_ack):

    print('Seq', packet.seqNumber, 'LastAck',last_ack)
    if(last_ack == -1 and packet.seqNumber == 0):
        last_ack = len(packet.data) + packet.seqNumber
        
    elif(len(packet.data) + int(packet.seqNumber) == int(last_ack) + len(packet.data)):
        last_ack = len(packet.data) + packet.seqNumber

    ack = p_server(last_ack)
    ack = pickle.dumps(ack)
    s.sendto(ack, add)
    return last_ack


# Funções do Cliente

# Envia os pacotes para o servidor
def send(s, host, port, window, lock):
  
    # Variaveis compartilhadas
    global max_packages
    max_packages = 2
    global print_lock
    print_lock = Condition()

    global aux_time
    aux_time = time()
    global aux_lock
    aux_lock = Condition()

    global end
    end = False

    print(aux_time)
    # Número de sequencia do pacote
    seqNumber = 0
    i = 0
    payloads = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789']
    
    while i != 15:
       
        # Demora aleatóriamente entre 0.6 e 1.2 para enviar um novo pacote
        sleep(random.uniform(0.6,1.2))
        # Envia pacotes com tamanho aleatório entre 1 e 9 de acordo com o indice da lista "payloads"
        data = payloads[random.randint(0,8)]
        packet = p_client(data, seqNumber)
        packet = pickle.dumps(packet)

        lock.acquire()
        if i > max_packages:
            lock.wait()
        lock.release()

        print_lock.acquire()
        print('Send', seqNumber, 'Size', len(data))
        print_lock.release()
        
        s.sendto(packet, (host, port))
        # Atualiza o número de sequencia
        seqNumber += len(data)

        lock.acquire()
        window[i%7] = (packet, seqNumber)
        lock.release()
        
        i += 1
    
    end = True
    print(end)

# Recebe os acks enviados pelo servidor
def recv_ack(s, host, port, window, lock, lasted_ack, packages_time):
 
    # Variaveis globais
    global max_packages
    max_packages = 2
    global print_lock
    print_lock = Condition()

    global aux_time
    global aux_lock
    aux_lock = Condition()

    rtt = 2.0
 
    while True:
        
        try:
            s.settimeout(rtt)

            # Recebe o pacote e o endereço do servidor
            data, add = s.recvfrom(4096)

            aux_lock.acquire()
            packages_time.append(time() - aux_time)   
            aux_time = time()
            aux_lock.release()
  
            packet = pickle.loads(data)

            print_lock.acquire()
            print('Ack  ', packet.ack)
            print_lock.release()
            
            # Flag para ver se o ack recebido é o esperado na janela
            ack_awaited = False

            for i in range(lasted_ack, max_packages + 1):
               
                lock.acquire()
                index = window[i%7]
                lock.release()

                if(packet.ack == index[1]):
                 
                    ack_awaited = True
                    lock.acquire()
                    
                    for j in range(lasted_ack, i + 1):
                       
                        window[j%7] = (None, None)
                        # Atualiza o ultimo ack recebido
                        lasted_ack += 1
                        max_packages += 1

                    lock.notify()
                    lock.release()

            if(ack_awaited == False):
                # Como foram recebidos ack duplicados a janela é reenviada
                print('Ack Duplicado')
                resend_window(s, host, port, window, lock, lasted_ack)

        except socket.error as error:
            # Se o houver um timeout a janela será reenviada
            print('Timeout')
            resend_window(s, host, port, window, lock, lasted_ack)

        empty_window = True
       
        for i in range(lasted_ack, max_packages + 1): 
            if window[i%7] != (None, None):
                empty_window = False
        
        if end == True and empty_window == True:
            print("Bye")
            break


# Reenvia toda a janela em caso de timeout e ack duplicado
def resend_window(s, host, port, window, lock, lasted_ack):
    
    print('Resend Window')
    print(lasted_ack, window)
   
    for i in range(max_packages - 1, lasted_ack - 1, -1):
        
        lock.acquire()
        index = window[i%7]
        packet = index[0]
        lock.release()      
        
        if(packet != None):
            s.sendto(packet, (host, port))
            sleep(0.2)
   
      
