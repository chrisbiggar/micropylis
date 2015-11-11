import struct

''' 

#  misc functions
'''
def create2dArray(width, height, fillValue=0):
    return [[fillValue for y in range(height)] for x in range(width)]

def writeShort(aFile, short):
    pass

def writeInt(aFile, int_):
    pass

def readShort(aFile):
    '''map is stored big endian'''
    return struct.unpack('>H',aFile.read(2))[0]

def readInt(aFile):
    '''map is stored big endian'''
    return struct.unpack('>I', aFile.read(4))[0]