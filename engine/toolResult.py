




class ToolResult(object):
    SUCCESS = 1
    NONE = 0
    UH_OH = -1 # invalid Position
    INSUFFICIENT_FUNDS = -2
    def __init__(self, value, cost):
        self.value = value
        self.cost = cost
    