'''
Created on Jan 22, 2016

@author: chris
'''
import array
from util import profile
TRUE = 1
FALSE = 0

class TwoDArray(object):
    '''
    Two dimentional interface to python's array.array()
    
    '''
    def __init__(self, typeCode, width, height, initilizer):
        self.array = array.array(typeCode, initilizer)
        self.width = width
        self.height = height
    
    def set(self, x, y, val):
        self.array[self.width * y + x] = val
    
    def get(self, x, y):
        return self.array[self.width * y + x]