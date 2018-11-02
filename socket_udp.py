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
    except socket.error as error:
        print("Failed to create socket. " + error)
        sys.exit()

    try:
        s.bind((host, port))
    except socket.error as error:
        print("Bind failed. Error Code :", error)
        sys.exit()

    return s

# Cria um socket cliente
def create_client(port):
   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as error:
        print("Failed to create socket. " + error)
        sys.exit()
    
    return s

# Funções do Servidor

# Função para receber os pacotes
def recv(s):
    
    global print_lock
    print_lock = Condition()

    # Ultimo ack recebido
    last_ack = -1
   
    while(1):
        # Recebe o pacote e o endereço do cliente
        data, add = s.recvfrom(4096)
        # Transforma o objeto de bytes no pacotes original
        packet = pickle.loads(data)
        
        print_lock.acquire()
        print("Pacote com número de sequência {} recebido".format(packet.seqNumber))
        print_lock.release()

        # Sorteia um número aleatorio de 1 a 8
        probability = random.randint(1,8)
        
        # Utiliza uma probalidade de 30% para que o pacote demore mais para responder
        if(probability < 4):
            # O servidor dorme um tempo aleatorio de 0.8 a 1.8
            sleep(random.uniform(0.8, 1.8))
            # Recebe o valor do ultimo ack confirmado
            last_ack = send_confirm(s, packet, add, last_ack)
        
        # Utiliza uma probalidade de 60% para que o pacote responda no tempo certo
        elif(probability < 10):
            # Recebe o valor do ultimo ack confirmado
            last_ack = send_confirm(s, packet, add, last_ack)
       
        # Utiliza uma probalidade de 10% para que o pacote se perca e não responda


# Função para enviar um ack para o cliente
def send_confirm(s, packet, add, last_ack):

    global print_lock
    print_lock = Condition()

    # Verifica se é o primeiro pacote recebido
    if(last_ack == -1 and packet.seqNumber == 0):
        # Atualiza o last_ack
        last_ack = len(packet.data) + packet.seqNumber

    # Verifica se o ack do pacote e o last_ack mas o tamanho do pacote são iguais    
    elif(len(packet.data) + int(packet.seqNumber) == int(last_ack) + len(packet.data)):
        # Atualiza o last_ack
        last_ack = len(packet.data) + packet.seqNumber

    # Constroi o pacote ack
    ack = p_server(last_ack)

    print_lock.acquire()
    print("Ack com valor {} enviado".format(last_ack))
    print_lock.release()

    # Transforma o pacote em um objeto de bytes para poder ser enviado
    ack = pickle.dumps(ack)
    s.sendto(ack, add)

    return last_ack


# Funções do Cliente

# Envia os pacotes para o servidor
def send(s, host, port, window, lock):
  
    # Variaveis compartilhadas
    global max_packages
    max_packages = 2
    global aux_time
    aux_time = time()
    global aux_lock
    aux_lock = Condition()
    global print_lock
    print_lock = Condition()

    # Variavel para controlar o fim do programa
    global end
    end = False

    # Número de sequencia do pacote
    seqNumber = 0
    # Pacotes enviados
    i = 0
    payloads = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789']
    
    # Envia 15 pacotes ao servidor
    while i != 15:
       
        # Demora aleatóriamente entre 0.6 e 1.2 para enviar um novo pacote
        sleep(random.uniform(0.6,1.2))
        # Envia pacotes com tamanho aleatório entre 1 e 9 de acordo com o indice da lista "payloads"
        data = payloads[random.randint(0,8)]
        # Constroi o pacote para ser enviado
        packet = p_client(data, seqNumber)
        # Transforma o pacote em um objeto de bytes
        packet = pickle.dumps(packet)

        lock.acquire()
        # Chega se a quantidades de pacotes enviados é maior do que max_package
        if i > max_packages:
            lock.wait()
        lock.release()
        
        s.sendto(packet, (host, port))
        
        print_lock.acquire()
        print("Pacote com número de sequência {} enviado".format(seqNumber))
        print_lock.release()

        # Atualiza o número de sequencia
        seqNumber += len(data)

        # Adiciona o pacote na janela
        lock.acquire()
        window[i%7] = (packet, seqNumber)
        lock.release()
        
        # Incrementa os pacotes enviados
        i += 1
    
    # Atualiza end
    end = True

# Recebe os acks enviados pelo servidor
def recv_ack(s, host, port, window, lock, lasted_ack, packages_time):
 
    # Variaveis compartilhadas
    global max_packages
    global aux_time
    global aux_lock
    aux_lock = Condition()
    global print_lock
    print_lock = Condition()

    rtt = 2.0
 
    while True:
        
        try:
            # Tempo que o cliente espera pela confirmação do ack
            s.settimeout(rtt)

            # Recebe o pacote e o endereço do servidor
            data, add = s.recvfrom(4096)

            # Adiciona o tempo de envio dos pacotes
            aux_lock.acquire()
            packages_time.append(time() - aux_time)   
            aux_time = time()
            aux_lock.release()

            # Transforma o objeto de bytes no pacotes original
            packet = pickle.loads(data)

            print_lock.acquire()
            print("Ack com número de sequência {} recebido".format(packet.ack))
            print_lock.release()
            
            # Flag para ver se o ack recebido é o esperado na janela
            ack_awaited = False

            # Percorre a janela de transmissão
            for i in range(lasted_ack, max_packages + 1):
                
                # Armazena o elemento (pacote, seqnumber) na variavel
                lock.acquire()
                index = window[i%7]
                lock.release()

                # Verifica se o ack recebido é igual ao numero de sequencia do pacote armazenado na janela
                if(packet.ack == index[1]):
                    # Ack recebido é o esperado
                    ack_awaited = True
                    lock.acquire()
                    
                    # Percorre a janela transformando em None os pacotes confirmados
                    for j in range(lasted_ack, i + 1):
                       
                        window[j%7] = (None, None)
                        # Atualiza o ultimo ack recebido
                        lasted_ack += 1
                        max_packages += 1

                    lock.notify()
                    lock.release()
            
            # Ack não é o esperado
            if(ack_awaited == False):
                print_lock.acquire()
                print("Ack duplicado")
                print_lock.release()

                # Como foram recebidos ack duplicados a janela é reenviada
                resend_window(s, host, port, window, lock, lasted_ack)

        except socket.error as error:
            print_lock.acquire()
            print("Timeout")
            print_lock.release()

            # Se o houver um timeout a janela será reenviada
            resend_window(s, host, port, window, lock, lasted_ack)

        # Variavel para verificar se todos os pacotes da janela foram confirmados
        empty_window = True
       
       # Percorre a janela verificando se existi pacotes não confirmados
        for i in range(lasted_ack, max_packages + 1): 
            if window[i%7] != (None, None):
                # Se houver atualiza a variavel para falso
                empty_window = False
        
        # Verifica se a janela está vazia e se o servidor parou de enviar pacotes
        if end == True and empty_window == True:
            break


# Reenvia toda a janela em caso de timeout e ack duplicado
def resend_window(s, host, port, window, lock, lasted_ack):
    print_lock.acquire()
    print("Reenviando janela de transmissão")
    print_lock.release()
    # Percorre a janela procurando o pacote que foi perdido
    for i in range(max_packages - 1, lasted_ack - 1, -1):
        
        lock.acquire()
        index = window[i%7]
        packet = index[0]
        lock.release()      
        
        # Se na posição existir um pacote diferente de None, o pacote é reenviado
        if(packet != None):
            s.sendto(packet, (host, port))
            sleep(0.2)
   
      
