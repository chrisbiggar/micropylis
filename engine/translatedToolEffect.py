'''
Created on Oct 24, 2015

@author: chris
'''


class TranslatedToolEffect(object):
    '''
    TranslatedToolEffect
    
    
    '''

    def __init__(self, base, dx, dy):
        self.base = base
        self.dX = dx
        self.dY = dy

    def getTile(self, x, y):
        return self.base.getTile(x + self.dX, y + self.dY)

    def setTile(self, x, y, tileValue):
        # print self.dX,self.dY
        self.base.setTile(x + self.dX, y + self.dY, tileValue)

    def spend(self, amount):
        self.base.spend(amount)

    def toolResult(self, tr):
        self.base.toolResult(tr)

    def makeSound(self, x, y, sound):
        self.base.makeSound(x, y, sound)
