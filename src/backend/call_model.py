class Call:
    def __init__(
        self,
        title,
        state,
        receiverName,
        receiverPhonenr,
        initiatorName,
        possibleDatetimes,
        result=None,
    ):
        self.title = title
        self.state = state
        self.receiverName = receiverName
        self.receiverPhonenr = receiverPhonenr
        self.initiatorName = initiatorName
        self.possibleDatetimes = possibleDatetimes
        self.result = result

    def setResult(self, result):
        self.result = result
