from __future__ import division
from random import randint

from engine import tileConstants
from engine.cityLocation import CityLocation
from engine.tileBehaviour import TileBehaviour
from engine.trafficGen import TrafficGen, ZoneType
from tileConstants import *
import tiles

RESIDENTIAL, HOSPITAL_CHURCH, COMMERCIAL, INDUSTRIAL, COAL, NUCLEAR, \
FIRESTATION, POLICESTATION, STADIUM_EMPTY, \
STADIUM_FULL, AIRPORT, SEAPORT = list(xrange(6, 18))

'''
    MapScanner

    Processing for individual zones/buildings.
'''


class MapScanner(TileBehaviour):


    def __init__(self, city, behaviour):
        super(MapScanner, self).__init__(city)
        self.behaviour = behaviour
        self.traffic = TrafficGen(city)
        self.ZeX = [0, -1, 0, 1, -1, 1, -1, 0, 1]  # build house
        self.ZeY = [0, -1, -1, -1, 0, 0, 1, 1, 1]  # build house

        self.DX = [0, 1, 0, -1]  # evalLot
        self.DY = [-1, 0, 1, 0]  # evalLot

        self.Brdr = [0, 3, 6, 1, 4, 7, 2, 5, 8] # doResidentialOut

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
            self.city.setTilePowerIndicator(self.x, self.y, True)

        if newPower and not oldPower:
            self.city.setTilePower(self.x, self.y, True)
            self.city.powerZone(self.x, self.y,
                                getZoneSizeFor(self.tile))
            self.city.setTilePowerIndicator(self.x, self.y, False)
        if not newPower and oldPower:
            self.city.setTilePower(self.x, self.y, False)
            self.city.shutdownZone(self.x, self.y, getZoneSizeFor(self.tile))
            self.city.setTilePowerIndicator(self.x, self.y, True)

        return newPower

    def zonePlop(self, base):
        assert isZoneCenter(base)

        bi = tiles.get(base).getBuildingInfo()
        assert bi is not None

        xOrg = self.x - 1
        yOrg = self.y - 1

        for y in xrange(yOrg, yOrg + bi.height):
            for x in xrange(xOrg, xOrg + bi.width):
                if not self.city.testBounds(x, y):
                    return False
                if isIndestructible(self.city.getTile(x, y)):
                    return False

        assert len(bi.members) == bi.width * bi.height
        i = 0
        for y in xrange(yOrg, yOrg + bi.height):
            for x in xrange(xOrg, xOrg + bi.width):
                self.city.setTile(x, y, bi.members[i])
                i += 1

        # refresh own tile property
        self.tile = self.city.getTile(self.x, self.y)

        self.setZonePower()
        return True

    def makeHospital(self):
        if self.city.needHospital > 0:
            self.zonePlop(HOSPITAL)
            self.city.needHospital = 0

        if self.city.needChurch > 0:
            self.zonePlop(CHURCH)
            self.city.needChurch = 0

    def doResidential(self):
        powerOn = self.checkZonePower()
        self.city.resZoneCount += 1

        if self.tile == RESCLR:
            tPop = self.city.doFreePop(self.x, self.y)
        else:
            tPop = residentialZonePop(self.tile)

        self.city.resPop += tPop

        if tPop > randint(0, 35):
            trafficGood = self.makeTraffic(ZoneType.RESIDENTIAL)
        else:
            trafficGood = 1

        if trafficGood == -1:
            value = self.getCRValue()
            self.doResidentialOut(tPop, value)
            return

        if self.tile == RESCLR or randint(0, 7) == 0:
            locValve = self.evalResidential(trafficGood)
            zScore = self.city.resValve + locValve

            #print "zScore: " + str(zScore)

            '''if not powerOn:
                zScore = -500'''

            whatisthis = randint(0, 0x10000 - 1) - 0x8000
            #print "what is this " + str(whatisthis)
            if zScore > -350 and zScore - 26380 > whatisthis:
                if tPop == 0 and randint(0,3) == 0:
                    self.makeHospital()
                    return

                value = self.getCRValue()
                self.doResidentialIn(tPop, value)
                #print "res zone in"


            elif zScore < 350 and zScore + 26380 > 25000:
                value = self.getCRValue()
                self.doResidentialOut(tPop, value)
                #print "res zone out"


    def doResidentialIn(self, pop, value):
        assert 0 <= value <= 3
        #print "do res in: " + str(pop) + " " + str(value)
        z = self.city.pollutionMem[self.y//2][self.x//2]
        if z > 128:
            return
        #print "z not higher than 128"
        if self.tile == RESCLR:
            if pop < 8:
                self.buildHouse(value)
                self.adjustROG(1)
                #print "build house"
                return

            #print "popden " + str(self.city.getPopulationDensity(self.x, self.y))
            if self.city.getPopulationDensity(self.x, self.y) > 64:
                self.residentialPlop(0, value)
                self.adjustROG(8)
                #print "residentialPlop"
                return

            #print "resclr but not build"
            return

        if pop < 40:
            #print "pop < 40: resPlop"
            self.residentialPlop(pop // 8 - 1, value)
            self.adjustROG(8)


    def doIndustrialIn(self, pop, value):
        if pop < 4:
            self.indPlop(pop, value)
            self.adjustROG(8)

    def doCommercialIn(self, pop, value):
        z = self.city.getLandValue(self.x, self.y) // 32
        if pop > z:
            return

        if pop < 5:
            self.comPlop(pop, value)
            self.adjustROG(8)

    def residentialPlop(self, density, value):
        base = int((value * 4 + density) * 9 + tileConstants.RZB)
        self.zonePlop(base)

    def comPlop(self, density, value):
        base = int((value * 5 + density) * 9 + CZB)
        self.zonePlop(base)

    def indPlop(self, density, value):
        base = int((value * 4 + density) * 9 + IZB)
        self.zonePlop(base)

    '''
        Consider the value of building a single-lot house at
        certain coordinates.
        Returns pos num for good place, zero or negative for bad place.
    '''
    def evalLot(self, x, y):
        aTile = self.city.getTile(x, y)
        if aTile != DIRT and (not isResidentialClear(aTile)):
            return -1

        score = 1

        for z in xrange(4):
            xx = x + self.DX[z]
            yy = y + self.DY[z]

            # look for road
            if self.city.testBounds(xx, yy):
                tmp = self.city.getTile(xx, yy)
                if isRoad(tmp) or isRail(tmp):
                    score += 1

        return score


    '''
        Build a single-lot house on the current residential zone.
    '''
    def buildHouse(self, value):
        assert 0 <= value <= 3

        bestLoc = 0
        hScore = 0
        for z in xrange(1, 9):
            xx = self.x + self.ZeX[z]
            yy = self.y + self.ZeY[z]

            if self.city.testBounds(xx, yy):
                score = self.evalLot(xx, yy)

                #print xx,yy,z,score

                if score != 0:
                    if score > hScore:
                        hScore = score
                        bestLoc = z

                    if score == hScore and randint(0,7) == 0:
                        bestLoc = z

        #print "---------------------------"
        #print bestLoc

        if bestLoc != 0:
            xx = self.x + self.ZeX[bestLoc]
            yy = self.y + self.ZeY[bestLoc]
            houseNumber = value * 3 + randint(0,2)
            #print xx,yy,houseNumber
            assert 0 <= houseNumber < 12

            assert self.city.testBounds(xx, yy)
            self.city.setTile(xx, yy, HOUSE + houseNumber)


    def doResidentialOut(self, pop, value):
        assert 0 <= value < 4

        if pop == 0:
            return

        if pop > 16:
            # downgrade to a lower-density full-size residential
            self.residentialPlop((pop - 24) // 8, value)
            self.adjustROG(-8)
            return

        if pop == 16:
            # downgrade from full-size zone to 8 little houses
            pwr = self.city.isTilePowered(self.x, self.y)
            self.city.setTile(self.x, self.y, RESCLR)
            self.city.setTilePower(self.x, self.y, pwr)

            for x in xrange(self.x - 1, self.x + 2):
                for y in xrange(self.y - 1, self.y + 2):
                    if self.city.testBounds(x, y):
                        if not (x == self.x and y == self.y):
                            houseNumber = value * 3 + randint(0,2)
                            self.city.setTile(x, y, HOUSE + houseNumber)

            self.adjustROG(-8)
            return

        if pop < 16:
            # remove one little houses
            self.adjustROG(-1)
            z = 0

            for x in xrange(self.x - 1, self.x + 2):
                for y in xrange(self.y - 1, self.y + 2):
                    if self.city.testBounds(x, y):
                        loc = self.city.map[y][x] & LOMASK
                        if LHTHR <= loc and loc <= HHTHR:
                            self.city.setTile(x, y, self.Brdr[z] + RESCLR - 4)
                            return
                    z += 1

    def doIndustrialOut(self, pop, value):
        if pop > 1:
            self.indPlop(pop - 2, value)
            self.adjustROG(-8)
        elif pop == 1:
            self.zonePlop(INDCLR)
            self.adjustROG(-8)

    def doCommercialOut(self, pop, value):
        if pop > 1:
            self.comPlop(pop - 2, value)
            self.adjustROG(-8)
        elif pop == 1:
            self.zonePlop(COMCLR)
            self.adjustROG(-8)



    '''
        Evaluates the zone value of the current res zone location
        Returns a int between -3000 and 300
         = more likely to shrink.
    '''
    def evalResidential(self, traf):
        if traf < 0:
            return -3000

        value = self.city.getLandValue(self.x, self.y)
        value -= self.city.pollutionMem[self.y//2][self.x//2]
        #print value

        if value < 0:
            value = 0
        else:
            value *= 32

        if value > 6000:
            value = 6000

        #return value - 3000
        return 200

    def evalIndustrial(self, traf):
        if traf < 0:
            return -1000
        else:
            return 0

    def evalCommercial(self, traf):
        if traf < 0:
            return -3000

        return self.city.comRate[self.y // 8][self.x // 8]


    '''
        Gets the land-value class (0-3) for the current
        residential or commercial zone location.
        :return integer from 0 to 3, 0 is the lowest-valued
        zone, and 3 is the highest-valued zone.
    '''
    def getCRValue(self):
        lVal = self.city.getLandValue(self.x, self.y)
        lVal -= self.city.pollutionMem[self.y//2][self.x//2]

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
        self.city.rateOGMem[self.y//8][self.x//8] += 4 * amount

    def doHospitalChurch(self):
        powerOn = self.checkZonePower()
        if self.tile == HOSPITAL:
            self.city.hospitalCount += 1

            if self.city.cityTime % 16 == 0:
                self.repairZone(HOSPITAL)
            if self.city.needHospital == -1:
                if randint(0,20) == 0:
                    self.zonePlop(RESCLR)
        elif self.tile == CHURCH:
            self.city.churchCount += 1

            if self.city.cityTime % 16 == 0:
                self.repairZone(CHURCH)
            if self.city.needChurch == -1:
                if randint(0,20) == 0:
                    self.zonePlop(RESCLR)

    def doCommercial(self):
        powerOn = self.checkZonePower()
        self.city.comZoneCount += 1

        tPop = commercialZonePop(self.tile)
        self.city.comPop = tPop

        if tPop > randint(0,5):
            trafficGood = self.makeTraffic(ZoneType.COMMERCIAL)
        else:
            trafficGood = 1

        if trafficGood == -1:
            value = self.getCRValue()
            self.doCommercialOut(tPop, value)
            return

        if randint(0,7) == 0:
            locValve = self.evalCommercial(trafficGood)
            zScore = self.city.comValve + locValve

            #print "zScore: " + str(zScore)

            '''if not powerOn:
                zScore = -500'''

            whatisthis = randint(0, 0x10000 - 1) - 0x8000
            #print "what is this " + str(whatisthis)
            if zScore > -350 and zScore - 26380 > whatisthis:
                value = self.getCRValue()
                self.doCommercialIn(tPop, value)
                #print "in"

            elif zScore < 350 and zScore + 26380 < whatisthis:
                value = self.getCRValue()
                self.doCommercialOut(tPop, value)
                #print "out"



    def doIndustrial(self):
        powerOn = self.checkZonePower()
        self.city.indZoneCount += 1

        tPop = industrialZonePop(self.tile)
        self.city.indPop += tPop

        if tPop > randint(0, 5):
            trafficGood = self.makeTraffic(ZoneType.INDUSTRIAL)
        else:
            trafficGood = 1

        if trafficGood == -1:
            self.doIndustrialOut(tPop, randint(0,1))
            return

        if randint(0,7) == 0:
            locValve = self.evalIndustrial(trafficGood)
            zScore = self.city.indValve + locValve

            #print "zScore: " + str(zScore)

            '''if not powerOn:
                zScore = -500'''

            whatisthis = randint(0, 0x10000 - 1) - 0x8000
            #print "what is this " + str(whatisthis)
            if zScore > -350 and zScore - 26380 > whatisthis:
                value = randint(0,1)
                self.doIndustrialIn(tPop, value)
                #print "in"

            elif zScore < 350 and zScore + 26380 < whatisthis:
                value = randint(0,1)
                self.doIndustrialOut(tPop, value)
                #print "out"


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
        self.city.fireStationCount += 1
        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.FIRESTATION)

    def doPoliceStation(self):
        powerOn = self.checkZonePower()
        self.city.policeCount += 1
        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.POLICESTATION)

        if powerOn:
            z = self.city.policeEffect
        else:
            z = self.city.policeEffect // 2

        self.traffic.mapX = self.x
        self.traffic.mapY = self.y
        if not self.traffic.findParameterRoad():
            z //= 2

        #self.city.policeMap[self.y // 8][self.x // 8] += z

    def doStadiumEmpty(self):
        powerOn = self.checkZonePower()
        self.city.stadiumCount += 1
        if self.city.cityTime % 16 == 0:
            self.repairZone(tileConstants.STADIUM)

    def doStadiumFull(self):
        powerOn = self.checkZonePower()
        self.city.stadiumCount += 1
        if self.city.cityTime % 16 == 0:
            self.repairZone(tileConstants.STADIUM)

    def doAirport(self):
        powerOn = self.checkZonePower()
        self.city.airportCount + 1
        if self.city.cityTime % 8 == 0:
            self.repairZone(tileConstants.AIRPORT)

    def doSeaport(self):
        powerOn = self.checkZonePower()
        self.city.seaportCount += 1
        if self.city.cityTime % 16 == 0:
            self.repairZone(tileConstants.PORT)

    '''
        Repairs a zones tile after that tile has been destroyed.
        Only works is tile is not rubble or zonecenter.
    '''
    def repairZone(self, base):

        assert isZoneCenter(base)

        powerOn = self.city.isTilePowered(self.x, self.y)

        bi = tiles.get(base).getBuildingInfo()
        assert bi is not None
        assert len(bi.members) == bi.width * bi.height

        xOrg = self.x - 1
        yOrg = self.y - 1
        i = 0
        for y in xrange(bi.height):
            for x in xrange(bi.width):
                x2 = xOrg + x
                y2 = yOrg + y

                ts = tiles.get(bi.members[i])
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