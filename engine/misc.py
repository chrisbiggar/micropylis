'''
Created on Sep 30, 2015

@author: chris
'''
import struct



        
''' misc functions for 
'''

def readShort(aFile):
    '''map is stored big endian'''
    return struct.unpack('>H',aFile.read(2))[0]

def readInt(aFile):
    '''map is stored big endian'''
    return struct.unpack('>I', aFile.read(4))[0]

def create2dArray(width, height):
    return [[0 for y in range(height)] for x in range(width)]