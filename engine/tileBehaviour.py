'''
Created on Oct 19, 2015

@author: chris
'''

class TileBehaviour(object):
    
    def __init__(self, city):
        self.city = city
        self.PRNG = city.PRNG
        
    def processTile(self, x, y):
        self.x = x
        self.y = y
        self.tile = self.city.getTile(x,y)
        self.apply()
        
    def apply(self):
        ''' abstract method '''
        pass
        