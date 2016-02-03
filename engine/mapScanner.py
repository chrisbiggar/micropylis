'''
Created on Oct 19, 2015

@author: chris
'''
from random import randint

from engine import tileConstants
from engine.cityLocation import CityLocation
from engine.tileBehaviour import TileBehaviour
from engine.trafficGen import TrafficGen, ZoneType
from tileConstants import (getZoneSizeFor, isZoneCenter, isRubble, isAnimated, isIndestructible,
                            RESCLR, residentialZonePop)
from tiles import Tiles

RESIDENTIAL, HOSPITAL_CHURCH, COMMERCIAL, INDUSTRIAL, COAL, NUCLEAR, \
FIRESTATION, POLICESTATION, STADIUM_EMPTY, \
STADIUM_FULL, AIRPORT, SEAPORT = range(6, 18)

'''
    MapScanner

    Processing for individual zones/buildings.
'''


class MapScanner(TileBehaviour):


    def __init__(self, city, behaviour):
        super(MapScanner, self).__init__(city)
        self.behaviour = behaviour
        self.traffic = TrafficGen(city)

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
            assert False  # invalid or unimplemened behaviour

    '''
        updates zone's power
    '''
    def checkZonePower(self):
        pwrFlag = self.setZonePower()

        if pwrFlag:
            self.city.poweredZoneCount += 1
        else:
            self.city.unpoweredZoneCount += 1

        return pwrFlag

    '''
        updates power bit for tiles according to powerMap
    '''
    def setZonePower(self):
        oldPower = self.city.isTilePowered(self.x, self.y)
        newPower = (self.tile == tileConstants.NUCLEAR or
                    self.tile == tileConstants.POWERPLANT or
                    self.city.hasPower(self.x, self.y))

        if not newPower:
            self.city.setTileIndicator(self.x, self.y, True)

        if newPower and not oldPower:
            self.city.setTilePower(self.x, self.y, True)
            self.city.powerZone(self.x, self.y,
                                getZoneSizeFor(self.tile))
            self.city.setTileIndicator(self.x, self.y, False)
        if not newPower and oldPower:
            self.city.setTilePower(self.x, self.y, False)
            self.city.shutdownZone(self.x, self.y, getZoneSizeFor(self.tile))
            self.city.setTileIndicator(self.x, self.y, True)

        return newPower

    def makeHospital(self):
        pass

    def doResidential(self):
        powerOn = self.checkZonePower()
        self.city.resZoneCount += 1

        if self.tile == RESCLR:
            tPop = self.city.doFreePop(self.x, self.y)
        else:
            tPop = residentialZonePop(self.tile)

        self.city.resPop += tPop

        if tPop > randint(0, 36): # does work same as java nextInt?
            trafficGood = self.makeTraffic(ZoneType.RESIDENTIAL)
        else:
            trafficGood = 1

        print "trafficgood " + str(trafficGood)

        if trafficGood == -1:
            value = self.getCRValue()
            self.doResidentialOut(tPop, value)
            return

        if self.tile == RESCLR or randint(0, 8) == 0:
            locValve = self.evalResidential(trafficGood)
            zScore = self.city.resValve + locValve

            print "zScore: " + str(zScore)

            '''if not powerOn:
                zScore = -500'''

            whatisthis = randint(0, 0x10000) - 0x8000
            print "what is this " + str(whatisthis)
            if zScore > -350 and zScore - 26380 > whatisthis:
                if tPop == 0 and randint(0,4) == 0:
                    self.makeHospital()
                    return

                value = self.getCRValue()
                self.doResidentialIn(tPop, value)
                print "in"


            elif zScore < 350 and zScore + 26380 > 25000:
                value = self.getCRValue()
                self.doResidentialOut(tPop, value)
                print "out"


    def doResidentialIn(self, pop, value):
        assert 0 <= value <= 3




    '''
        Consider the value of building a single-lot house at
        certain coordinates.
        Returns pos num for good place, zero or negative for bad place.
    '''
    def evalLot(self, x, y):
        pass


    '''
        Build a single-lot house on the current residential zone.
    '''
    def buildHouse(self, value):
        pass


    def doResidentialOut(self, pop, value):
        assert 0 <= value < 4

    '''
        Evaluates the zone value of the current res zone location
        Returns a int between -3000 and 3000.
        Higher = more likely to grow, lower = more likely to shrink.
    '''
    def evalResidential(self, traf):
        if traf < 0:
            return -3000

        value = self.city.getLandValue(self.x, self.y)
        value -= self.city.pollutionMem[self.y/2][self.x/2]
        #print value

        if value < 0:
            value = 0
        else:
            value *= 32

        if value > 6000:
            value = 6000

        #return value - 3000
        return 200


    '''
        Gets the land-value class (0-3) for the current
        residential or commercial zone location.
        :return integer from 0 to 3, 0 is the lowest-valued
        zone, and 3 is the highest-valued zone.
    '''
    def getCRValue(self):
        lVal = self.city.getLandValue(self.x, self.y)
        lVal -= self.city.pollutionMem[self.y/2][self.x/2]

        if lVal < 30:
            return 0
        if lVal < 80:
            return 1
        if lVal < 150:
            return 2

        return 3


    '''
        Record a zone's population change to the rate-of-growth map.
        +/- 1 amount corresponds to one little house.
        +/- 8 amount corresponds to a full-size zone.
    '''
    def adjustROG(self, amount):
        self.city.rateOGMem[self.y/2][self.x/2] += 4 * amount

    def doHospitalChurch(self):
        powerOn = self.checkZonePower()

    def doCommercial(self):
        powerOn = self.checkZonePower()

    def doIndustrial(self):
        powerOn = self.checkZonePower()

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
        powerOn = self.checkZonePower()

        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.FIRESTATION)

    def doPoliceStation(self):
        powerOn = self.checkZonePower()

        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.POLICESTATION)

    def doStadiumEmpty(self):
        powerOn = self.checkZonePower()

        if self.city.cityTime % 16 == 0:
            self.repairZone(tileConstants.STADIUM)

    def doStadiumFull(self):
        powerOn = self.checkZonePower()

    def doAirport(self):
        powerOn = self.checkZonePower()

        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.AIRPORT)

    def doSeaport(self):
        powerOn = self.checkZonePower()

        if self.city.cityTime % 16 == 0:
            self.repairZone(tileConstants.PORT)

    '''
        Repairs a zones tile after that tile has been destroyed.
        Only works is tile is not rubble or zonecenter.
    '''
    def repairZone(self, base):

        assert isZoneCenter(base)

        powerOn = self.city.isTilePowered(self.x, self.y)

        bi = Tiles().get(base).getBuildingInfo()
        assert bi is not None
        assert len(bi.members) == bi.width * bi.height

        xOrg = self.x - 1
        yOrg = self.y - 1
        i = 0
        for y in xrange(bi.height):
            for x in xrange(bi.width):
                x2 = xOrg + x
                y2 = yOrg + y

                ts = Tiles().get(bi.members[i])
                if powerOn and ts.onPower is not None:
                    ts = ts.onPower

                if self.city.testBounds(x2, y2):
                    thCh = self.city.getTile(x2, y2)
                    if not (isIndestructible(thCh)
                            or isAnimated(thCh)
                            or isRubble(thCh)
                            or isZoneCenter(thCh)):
                        self.city.setTile(x2, y2, ts.tileNum)
                    i += 1

    '''
        1 if traffic passed, 0 if failed, -1 no roads found
    '''
    def makeTraffic(self, zoneType):
        self.traffic.mapX = self.x
        self.traffic.mapY = self.y
        self.traffic.sourceZone = zoneType
        return self.traffic.makeTraffic()