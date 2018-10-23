import socket
import sys
import time
from payload import *
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


def create_client(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket Created")
    except socket.error as error:
        # print("Failed to create socket. Error code:" + str(error[0]) + 'Message' + error[1])
        sys.exit()
    return s


def recv(s, port):

    while(1):
        data, add = s.recvfrom(4096)
        print(str(pickle.loads(data).ack))
        packet = pickle.loads(data)
        send_confirm(s, packet, add)
    # s.close()


def send_confirm(s, header, port):
    ack = payload("ack", header.ack, header.seqNumber,
                  header.destiny, header.font)
    orig = ack.font
    # print(orig, port)
    ack = pickle.dumps(ack)
    s.sendto(ack, port)


def send(s, host_s, port, host_c):
    seqNumber = 0
    while True:
        data = input("Enter message to send : ")
        ack = len(data) + seqNumber
        print('send', ack)
        msg = payload(data, ack, seqNumber, host_c, host_s)
        msg = pickle.dumps(msg)
        s.sendto(msg, (host_s, port))
    
def recv_ack(s, host_s, port, host_c):
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
            print('recv', packet.ack)

        except socket.error as error:
            #print("Error Code :" + str(err) + "Message" + err)
            # sys.exit()
            pass
        rtt = time.time() - now
