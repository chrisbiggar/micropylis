'''
Created on Oct 19, 2015

@author: chris
'''
from engine.tileBehaviour import TileBehaviour


class TerrainBehaviour(TileBehaviour):
    
    def __init__(self, city, b):
        super(self, TerrainBehaviour).__init(city)
        self.behaviour = b
        
    def apply(self):
        pass
    
    def doFire(self):
        pass
    
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
    
    
    
    
    
    
    
    
    
    
    