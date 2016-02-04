
MIN_LEVEL = 0
MAX_LEVEL = 2

def isValid(lev):
    return MIN_LEVEL <= lev <= MAX_LEVEL

def getStartingFunds(lev):
    if lev == 0:
        return 20000
    elif lev == 1:
        return 10000
    elif lev == 2:
        return 5000
    else:
        raise Exception("Unexpected Game Level")