import socket
import sys
from time import sleep, time
from p_client import *
from p_server import *
import pickle
import string
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
        sleep(5)
        # update the ack number
        last_ack = send_confirm(s, packet, add, last_ack)

    # s.close()

# send a ack to the client
def send_confirm(s, packet, add, last_ack):

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

    while True:
        
        print_lock.acquire()
        data = input("Enter message to send : ")
        try:
            print_lock.release()
        except:
            pass

        #print('send', seqNumber)
        packet = p_client(data, seqNumber,host)
        packet = pickle.dumps(packet)
        s.sendto(packet, (host, port))
        seqNumber += len(data)

        print_lock.acquire()
        print("Max I: ",max_packages)
        print_lock.release()

        lock.acquire()
        if i > max_packages:
            lock.notify()
            lock.wait()

        else: 
            window.insert(i%7,(packet, seqNumber))
            i += 1
        
        lock.release()
        #print(window)   
        print_lock.acquire()
        print("Max F: ",max_packages)
        print_lock.release()
def recv_ack(s, window, lock, lasted_ack):
  
    global max_packages
    max_packages = 2
    global print_lock
    print_lock = Condition()

    rtt = 0.1
    aux = time()
    #while (time.time() - aux) < 5:

    while True:
        now = time()
        try:
            # print(host_s, port)
            s.settimeout(rtt)
            data, add = s.recvfrom(4096)
            packet = pickle.loads(data)

            print_lock.acquire()
            print("Max ack I: ",max_packages)
            print_lock.release()
           

            for i in range(lasted_ack, max_packages + 1):
                lock.acquire()
                t = window[i%7]
                lock.release()
                #print_lock.acquire()
                #print("t[1]",t[1])
                #print_lock.release()
    
                if(packet.ack == t[1]):
                    lock.acquire()
                    for i in range(lasted_ack, i + 1):
                        window[i%7] = (None, None)
                        #print(lasted_ack)
                        lasted_ack += 1
                        max_packages += 1

                        print_lock.acquire()
                        print("Max ack F: ",max_packages)
                        print_lock.release()

                    #print('Ack recebido', packet.ack)
                    lock.notify()
                    lock.release()

        except socket.error as error:
            #print("Error Code :" + str(err) + "Message" + err)
            # sys.exit()
            pass
        rtt = time() - now
