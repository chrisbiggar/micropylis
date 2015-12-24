'''
Created on Oct 19, 2015

@author: chris
'''
from random import randint
from engine.tileBehaviour import TileBehaviour
from engine import tileConstants
from engine.tileConstants import isCombustible, isZoneCenter

FIRE,FLOOD,RADIOACTIVE,ROAD,RAIL,EXPLOSION = range(6)


class TerrainBehaviour(TileBehaviour):
    
    def __init__(self, city, b):
        super(TerrainBehaviour,self).__init__(city)
        self.behaviour = b
        
    def apply(self):
        if self.behaviour == FIRE:
            self.doFire()
        elif self.behaviour == FLOOD:
            self.doFlood()
        elif self.behaviour == RADIOACTIVE:
            self.doRadioactiveTile()
        elif self.behaviour == ROAD:
            self.doRoad()
        elif self.behaviour == RAIL:
            self.doRail()
        elif self.behaviour == EXPLOSION:
            self.doExplosion()
        else:
            assert False
              
    def doFire(self):
        self.city.firePop += 1
        
        if randint(0,3) != 0:
            return
        
        dx = [0,1,0,-1]
        dy = [-1,0,1,0]
        
        for dir in xrange(4):
            if randint(0,7) == 0:
                x = self.x + dx[dir]
                y = self.y + dy[dir]
                if not self.city.testBounds(x,y):
                    continue
                
                tile = self.city.getTile(x,y)
                if isCombustible(tile):
                    if isZoneCenter(tile):
                        #self.city.kilZone()
                        #TODO make explosionx
                        pass
                    self.city.setTile(x, y, tileConstants.FIRE + randint(0,3))
                 
        #TODO fire station coverage

        
        '''if (randint(0,rate) == 0) {
            city.setTile(xpos, ypos, (char)(RUBBLE + PRNG.nextInt(4)));
        }'''
    
    def doFlood(self):
        pass
    
    def doRadioactiveTile(self):
        pass
    
    def doRoad(self):
        city = self.city
        
        city.roadTotal += 1
        
        if city.roadEffect < 30:
            # deteriorating roads
            
            pass
    
    def doRail(self):
        pass
    
    def doExplosion(self):
        pass
    
    
    
    
    
    
    
    
    
    
    