class p_client():
    def __init__(self, data, seqNumber):
        self.data = data.encode()
        self.seqNumber = seqNumber

