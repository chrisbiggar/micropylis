'''
Created on Oct 19, 2015

@author: chris
'''
from engine.tileBehaviour import TileBehaviour

RESIDENTIAL,HOSPITAL_CHURCH,COMMERCIAL,INDUSTRIAL,COAL,NUCLEAR,\
FIRESTATION,POLICESTATION,STADIUM_EMPTY,\
STADIUM_FULL,AIRPORT,SEAPORT = range(6,18)


class MapScanner(TileBehaviour):
    '''
    classdocs
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
        pass
    
    def doNuclearPower(self):
        pass
    
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
        