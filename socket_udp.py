import socket
import sys
import time
from p_client import *
from p_server import *
import pickle
import string



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


def create_client(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        # print("Failed to create socket. Error code:" + str(error[0]) + 'Message' + error[1])
        sys.exit()
    return s

# Server
def recv(s):
    last_ack = -1
    while(1):
        data, add = s.recvfrom(4096)
        packet = pickle.loads(data)
        last_ack = send_confirm(s, packet, add, last_ack)

    # s.close()


def send_confirm(s, packet, add, last_ack):

    if(last_ack == -1 and packet.seqNumber == 0):
        last_ack = len(packet.data) + packet.seqNumber
        # print('primeiro', last_ack)
    elif(len(packet.data) + int(packet.seqNumber) == int(last_ack) + len(packet.data)):
        # print(len(packet.data) + packet.seqNumber)
        #packet.ack = len(packet.data) + packet.seqNumber
        last_ack = len(packet.data) + packet.seqNumber

    print(last_ack)
    ack = p_server(last_ack)
    ack = pickle.dumps(ack)
    s.sendto(ack, add)
    return last_ack


# Client
def send(s, host, port, window, lock, max_packages):
    seqNumber = 0
    i = 0

    while True:
        data = input("Enter message to send : ")
        print('send', seqNumber)
        packet = p_client(data, seqNumber,host)
        packet = pickle.dumps(packet)
        s.sendto(packet, (host, port))
        seqNumber += len(data)

        lock.acquire()
        print(max_packages)
        if i <= max_packages:
            window.insert(i%7,(packet, seqNumber))
            i += 1
        lock.release()
        #print(window)   
    
def recv_ack(s, window, lock, lasted_ack, max_packages):
    rtt = 0.1
    aux = time.time()
    #while (time.time() - aux) < 5:
    while True:
        now = time.time()
        try:
            # print(host_s, port)
            s.settimeout(rtt)
            data, add = s.recvfrom(4096)
            packet = pickle.loads(data)

            for i in range(lasted_ack, max_packages + 1):
                t = window[i%7]
                print(t[1])
                if(packet.ack == t[1]):
                    lock.acquire()
                    for i in range(lasted_ack, i + 1):
                        window[i%7] = (None, None)
                        print(lasted_ack)
                        lasted_ack += 1
                        max_packages += 1
                    print('Ack recebido', packet.ack)
                    lock.release()

        except socket.error as error:
            #print("Error Code :" + str(err) + "Message" + err)
            # sys.exit()
            pass
        rtt = time.time() - now
