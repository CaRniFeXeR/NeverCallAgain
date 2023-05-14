class DB_Handler:
    def init(self):
        self.calls = []

    def insertNewCall(self, call):
        self.calls.append(call)

    def getAllCalls(self):
        return self.calls
