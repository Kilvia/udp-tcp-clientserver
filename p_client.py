class p_client():
    def __init__(self, data, seqNumber, host_s):
        self.data = data.encode()
        self.seqNumber = seqNumber
        self.destiny = host_s
