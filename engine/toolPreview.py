'''
Created on Oct 22, 2015

@author: chris
'''
import util
from toolResult import ToolResult
from engine.tileConstants import CLEAR
from engine.cityRect import CityRect
from util import create2dArray


class ToolPreview(object):

    def __init__(self):
        self.offsetX = 0 #?
        self.offsetY = 0 #?
        self.tiles = create2dArray(0,0,CLEAR)
        # sounds here
        self.toolResult = ToolResult.NONE
        self.cost = 0
        
        
    def getTile(self, dx, dy):
        if self.inRange(dx, dy):
            return self.tiles[self.offsetY+dy][self.offsetX+dx]
        else:
            return CLEAR
    
    def getBounds(self):
        return CityRect(
                        -self.offsetX,
                        -self.offsetY,
                        self.getWidth(),
                        self.getHeight())
    
    def getWidth(self):
        if len(self.tiles) != 0:
            return len(self.tiles[0])
        else:
            return 0
    
    def getHeight(self):
        return len(self.tiles)
    
    def inRange(self, dx, dy):
        return self.offsetY + dy >= 0 and\
                self.offsetY + dy < self.getHeight() and\
                self.offsetX + dx >= 0 and\
                self.offsetX + dx < self.getWidth()
    
    def expandTo(self, dx, dy):
        if self.tiles is None or len(self.tiles) == 0:
            self.tiles = create2dArray(1,1,CLEAR)
            self.offsetX = -dx
            self.offsetY = -dy
            return
        
        for i in xrange(len(self.tiles)):
            orig = self.tiles[i]
            
            if self.offsetX + dx >= len(orig):
                newLen = self.offsetX + dx + 1
                new = [CLEAR] * newLen
                for i2 in xrange(len(orig)):
                    new[i2] = orig[i2]
                for i2 in xrange(len(orig)+1,newLen):
                    new[i2] = CLEAR
                self.tiles[i] = new
            elif self.offsetX + dx < 0:
                #TODO (change roads ref) when roads connect together and fixTile() goes
                # left of tool starting X this branch happens
                addl = -(self.offsetX + dx)
                newLen = len(orig) + addl
                new = [CLEAR] * newLen
                for i2 in xrange(len(orig)):
                    new[i2+addl] = orig[i2]
                for i2 in xrange(addl):
                    new[i2] = CLEAR
                self.tiles[i] = new
                
        if self.offsetX + dx < 0:
            add1 = -(self.offsetX + dx)
            self.offsetX += add1
            
        width = len(self.tiles[0])
        if self.offsetY + dy >= len(self.tiles):
            # just increase size, copy array adding clear as post padding
            
            newLen = self.offsetY + dy + 1
            newTiles = create2dArray(newLen,width,CLEAR)
            
            for y in xrange(len(self.tiles)):
                for x in xrange(len(self.tiles[0])):
                    newTiles[y][x] = self.tiles[y][x]
                    
            for y in xrange(len(self.tiles)+1,len(newTiles)):
                for x in xrange(len(newTiles[0])):
                    newTiles[y][x] = CLEAR
            self.tiles = newTiles
            
        if self.offsetY + dy < 0:
            # when roads connect together and fixTile() goes
            # above of tool starting Y this branch happens
            addl = -(self.offsetY + dy)
            newLen = len(self.tiles) + addl
            newTiles = create2dArray(newLen,width,CLEAR)
            
            for y in xrange(len(self.tiles)):
                for x in xrange(len(self.tiles[0])):
                    newTiles[y+addl][x] = self.tiles[y][x]
                    
            for y in xrange(addl):
                for x in xrange(len(newTiles[0])):
                    newTiles[y][x] = CLEAR
                    
            self.tiles = newTiles
            self.offsetY += addl
            
    
    ''' def makeSound '''
    
    
    
   
    def setTile(self, dx, dy, tileValue):
        self.expandTo(dx,dy)
        self.tiles[self.offsetY+dy][self.offsetX+dx] = tileValue
    
    def spend(self, amount):
        self.cost += amount
    
    def setToolResult(self, tr):
        self.toolResult = tr
        