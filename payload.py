class payload():
    def __init__(self, data, ack, seqNumber, host_c, host_s):
      
        self.data = data.encode()
        self.ack = ack
        self.seqNumber = seqNumber
        self.font = host_c
        self.destiny = host_s
