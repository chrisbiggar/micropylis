'''
Created on Oct 18, 2015

@author: chris
'''
import build
from build import makeTiles


def main():
    makeTiles.make(8, 'res/tiles.rc', 'res/tiles')
    makeTiles.make(16, 'res/tiles.rc', 'res/tiles')
    makeTiles.make(32, 'res/tiles.rc', 'res/tiles')
    
    print "Done build."


if __name__ == '__main__':
    main()