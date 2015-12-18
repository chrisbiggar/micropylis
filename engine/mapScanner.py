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
    contains the processing algorithms for the zones
    
    
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
        
        if not newPower:
            self.city.setTileIndicator(self.x,self.y,True)
        
        if newPower and not oldPower:
            self.city.setTilePower(self.x, self.y, True)
            self.city.powerZone(self.x, self.y, 
                                getZoneSizeFor(self.tile))
            self.city.setTileIndicator(self.x,self.y,False)
        if not newPower and oldPower:
            self.city.setTilePower(self.x, self.y, False)
            self.city.shutdownZone(self.x, self.y, getZoneSizeFor(self.tile))
            self.city.setTileIndicator(self.x,self.y,True)
        
        return newPower  
        
          
    def doResidential(self):
        powerOn = self.checkZonePower()
        #print "dores"
        
    
    def doHospitalChurch(self):
        powerOn = self.checkZonePower()
        
    
    def doCommercial(self):
        powerOn = self.checkZonePower()
    
    def doIndustrial(self):
        powerOn = self.checkZonePower()
    
    def doCoalPower(self):
        #print "docoal"
        powerOn = self.checkZonePower()
        self.city.coalCount += 1
        if self.city.cityTime % 8 == 0:
            #self.repairZone(tileConstants.POWERPLANT)
            pass
        self.city.powerPlants.append(CityLocation(self.x, self.y))
    
    def doNuclearPower(self):
        powerOn = self.checkZonePower()
        self.city.nuclearCount += 1
        if self.city.cityTime % 8 == 0:
            #self.repairZone(tileConstants.NUCLEAR)
            pass
        self.city.powerPlants.append(CityLocation(self.x, self.y))
    
    def doFireStation(self):
        powerOn = self.checkZonePower()
    
    def doPoliceStation(self):
        powerOn = self.checkZonePower()
    
    def doStadiumEmpty(self):
        powerOn = self.checkZonePower()
    
    def doStadiumFull(self):
        powerOn = self.checkZonePower()
    
    def doAirport(self):
        powerOn = self.checkZonePower()
    
    def doSeaport(self):
        powerOn = self.checkZonePower()
    
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
        for y in xrange(bi.height):
            for x in xrange(bi.width):
                xx = xOrg + x
                yy = yOrg + y
                
                ts = Tiles().get(bi.members[i])
                if powerOn and ts.onPower is not None:
                    ts = ts.onPower
                
                if self.city.testBounds(xx,yy):
                    thCh = self.city.getTile(xx,yy)
                    if isZoneCenter(thCh):
                        continue
                    
                    if tileConstants.isAnimated(thCh):
                        continue
                    
                    '''if isRubble(thCh):
                        continue'''
                   
                    #if is
                    
                    self.city.setTile(xx,yy,ts.tileNum)
                i += 1












    
    
        