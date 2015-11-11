'''
Created on Oct 29, 2015

@author: chris
'''
from engine import tileConstants


def test():
    tile = tileConstants.HRAIL
    
    print tileConstants.isRail(tile)



if __name__ == '__main__':
    test()