import socket
import sys
from time import sleep, time
from p_client import *
from p_server import *
import pickle
import string
import random
from threading import Condition

# create a socket server 
def create_server(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        # print("Failed to create socket. Error code:" + str(error[0]) + 'Message' + error[1])
        sys.exit()

    try:
        s.bind((host, port))
    except socket.error as error:
        print("Bind failed. Error Code :", error)
        sys.exit()

    print("Socket bind complete")

    return s
# create a socket client
def create_client(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        # print("Failed to create socket. Error code:" + str(error[0]) + 'Message' + error[1])
        sys.exit()
    return s

# Server

# function to receive packages
def recv(s):
    # ack number
    last_ack = -1
   
    while(1):
        # receive the package and the address
        data, add = s.recvfrom(4096)
        packet = pickle.loads(data)

        probability = random.randint(1,9)
        # Utiliza uma probalidade de 30% para que o pacote demore mais para responder
        if(probability < 4):
            sleep(random.uniform(0.8, 1.8))
        # Utiliza uma probalidade de 50% para que o pacote responda no tempo certo
        elif(probability < 9):
            last_ack = send_confirm(s, packet, add, last_ack)
        # Utiliza uma probalidade de 20% para que o pacote se perca e não responda

        # update the ack number
        

    # s.close()

# send a ack to the client
def send_confirm(s, packet, add, last_ack):
    print('Seq', packet.seqNumber, 'LastAck',last_ack)
    if(last_ack == -1 and packet.seqNumber == 0):
        last_ack = len(packet.data) + packet.seqNumber
        # print('primeiro', last_ack)
    elif(len(packet.data) + int(packet.seqNumber) == int(last_ack) + len(packet.data)):
        # print(len(packet.data) + packet.seqNumber)
        #packet.ack = len(packet.data) + packet.seqNumber
        last_ack = len(packet.data) + packet.seqNumber

    #print(last_ack)
    ack = p_server(last_ack)
    ack = pickle.dumps(ack)
    s.sendto(ack, add)
    return last_ack


# Client
def send(s, host, port, window, lock):
    global max_packages
    max_packages = 2
    global print_lock
    print_lock = Condition()
    seqNumber = 0
    i = 0
    payloads = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789']
    while True:
        
        # print_lock.acquire()
        # data = input("Enter message to send : ")
        # try:
        #     print_lock.release()
        # except:
        #     pass

        # Demora aleatóriamente entre 0.6 e 1.2 para enviar um novo pacote
        sleep(random.uniform(0.6,1.2))
        # Envia pacotes com tamanho aleatório entre 1 e 9 de acordo com o indice da lista "payloads"
        data = payloads[random.randint(0,8)]
        #print('send', seqNumber)
        packet = p_client(data, seqNumber,host)
        packet = pickle.dumps(packet)
        
        # print_lock.acquire()
        # print("S Max I: ",max_packages)
        # print_lock.release()

        lock.acquire()
        if i > max_packages:
            #lock.notify()
            lock.wait()
        lock.release()
        
        lock.acquire()
        print_lock.acquire()
        print('Send', seqNumber, 'Size', len(data))
        print_lock.release()
        s.sendto(packet, (host, port))
        seqNumber += len(data)
        window[i%7] = (packet, seqNumber)
        i += 1
        lock.release()

        #print(window)   
        # print_lock.acquire()
        # print("S Max F: ",max_packages)
        # print_lock.release()

def recv_ack(s, host, port, window, lock, lasted_ack):
  
    global max_packages
    max_packages = 2
    global print_lock
    print_lock = Condition()

    rtt = 2.0
    # aux = time()
    #while (time.time() - aux) < 5:

    while True:
        # now = time()
        try:
            # print(host_s, port)
            s.settimeout(rtt)
            data, add = s.recvfrom(4096)
            packet = pickle.loads(data)

            print_lock.acquire()
            # print("R Max ack I: ",max_packages)           
            # print('In', window)
            print('Ack  ', packet.ack)
            print_lock.release()
            
            # Flag para ver se o ack recebido não é o esperado na janela
            ack_awaited = False
            for i in range(lasted_ack, max_packages + 1):
                lock.acquire()
                index = window[i%7]
                lock.release()
                #print_lock.acquire()
                #print("t[1]",t[1])
                #print_lock.release()
    
                if(packet.ack == index[1]):
                    ack_awaited = True
                    lock.acquire()
                    # print_lock.acquire()
                    # print("R",window)
                    # print_lock.release()
                    for j in range(lasted_ack, i + 1):
                        window[j%7] = (None, None)
                        #print(lasted_ack)
                        lasted_ack += 1
                        max_packages += 1

                        # print_lock.acquire()
                        # print("R Max ack F: ",max_packages)
                        # print_lock.release()

                    #print('Ack recebido', packet.ack)
                    lock.notify()
                    lock.release()
            if(ack_awaited == False):
                print('Ack Duplicado')
                resend_window(s, host, port, window, lock, lasted_ack)

        except socket.error as error:
            print('Timeout')
            resend_window(s, host, port, window, lock, lasted_ack)
            #print("Error Code :" + str(err) + "Message" + err)
            # sys.exit()
            pass
        # rtt = time() - now

# Reenvia toda a janela em caso de timeout e ack duplicado
def resend_window(s, host, port, window, lock, lasted_ack):
    print('Resend Window')
    print(lasted_ack, window)
    lock.acquire()
    for i in range(max_packages - 1, lasted_ack - 1, -1):
        # print(window[i%7])
        sleep(0.2)
        index = window[i%7]
        packet = index[0]
        if(packet != None):
            s.sendto(packet, (host, port))
    lock.release()    
