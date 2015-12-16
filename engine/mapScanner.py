'''
Created on Oct 19, 2015

@author: chris
'''
from engine.tileBehaviour import TileBehaviour
from engine import tileConstants
from tileConstants import getZoneSizeFor
from tileConstants import isZoneCenter
from engine.cityLocation import CityLocation
from tiles import Tiles

RESIDENTIAL,HOSPITAL_CHURCH,COMMERCIAL,INDUSTRIAL,COAL,NUCLEAR,\
FIRESTATION,POLICESTATION,STADIUM_EMPTY,\
STADIUM_FULL,AIRPORT,SEAPORT = range(6,18)


class MapScanner(TileBehaviour):
    '''
    
    
    
    '''


    def __init__(self, city, behaviour):
        super(MapScanner,self).__init__(city)
        self.behaviour = behaviour
        #self.traffic = TrafficGen()
    
    def apply(self):
        if self.behaviour == RESIDENTIAL:
            self.doResidential()
        elif self.behaviour == COMMERCIAL:
            self.doCommercial()
        elif self.behaviour == HOSPITAL_CHURCH:
            self.doHospitalChurch()
        elif self.behaviour == INDUSTRIAL:
            self.doIndustrial()
        elif self.behaviour == COAL:
            self.doCoalPower()
        elif self.behaviour == NUCLEAR:
            self.doNuclearPower()
        elif self.behaviour == FIRESTATION:
            self.doFireStation()
        elif self.behaviour == POLICESTATION:
            self.doPoliceStation()
        elif self.behaviour == STADIUM_EMPTY:
            self.doStadiumEmpty()
        elif self.behaviour == STADIUM_FULL:
            self.doStadiumFull()
        elif self.behaviour == AIRPORT:
            self.doAirport()
        elif self.behaviour == SEAPORT:
            self.doSeaport()
        else:
            assert False
            
            
    def checkZonePower(self):
        ''' updates zone's power '''
        pwrFlag = self.setZonePower()
        
        if pwrFlag:
            self.city.poweredZoneCount += 1
        else:
            self.city.unpoweredZoneCount += 1
            
        return pwrFlag
    
    def setZonePower(self):
        ''' updates power bit for tiles according to powerMap'''
        oldPower = self.city.isTilePowered(self.x, self.y)
        newPower = ( self.tile == tileConstants.NUCLEAR or
                     self.tile == tileConstants.POWERPLANT or
                     self.city.hasPower(self.x,self.y))
        
        if newPower and not oldPower:
            self.city.setTilePower(self.x, self.y, True)
            self.city.powerZone(self.x, self.y, 
                                getZoneSizeFor(self.tile))
        if not newPower and oldPower:
            self.city.setTilePower(self.x, self.y, False)
            self.city.shutdownZone(self.x, self.y, getZoneSizeFor(self.tile))
        
        return newPower  
        
          
    def doResidential(self):
        #print "process res"
        pass
    
    def doHospitalChurch(self):
        pass
    
    def doCommercial(self):
        pass
    
    def doIndustrial(self):
        pass
    
    def doCoalPower(self):
        powerOn = self.checkZonePower()
        self.city.coalCount += 1
        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.POWERPLANT)
        self.city.powerPlants.append(CityLocation(self.x, self.y))
    
    def doNuclearPower(self):
        powerOn = self.checkZonePower()
        self.city.nuclearCount += 1
        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.NUCLEAR)
        self.city.powerPlants.append(CityLocation(self.x, self.y))
    
    def doFireStation(self):
        pass
    
    def doPoliceStation(self):
        pass
    
    def doStadiumEmpty(self):
        pass
    
    def doStadiumFull(self):
        pass
    
    def doAirport(self):
        pass
    
    def doSeaport(self):
        pass
    
    def repairZone(self, base):
        '''  '''
        assert isZoneCenter(base)
        
        powerOn = self.city.isTilePowered(self.x, self.y)
        
        bi = Tiles().get(base).getBuildingInfo()
        assert bi is not None
        
        xOrg = self.x - 1
        yOrg = self.y - 1
        
        assert len(bi.members) == bi.width * bi.height
        i = 0
    
    
        