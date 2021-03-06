'''
    main engine module
    
'''
from __future__ import division
import ConfigParser
from random import randint

from pyglet.event import EventDispatcher
from . import tiles
from .cityLocation import CityLocation
from engine.terrainBehaviour import TerrainBehaviour
from engine.tileConstants import *
from .micropylisMessage import MicropylisMessage
from .mapScanner import MapScanner
from util import readShort, readInt, create2dArray
from . import gameLevel


class CityBudget(object):
    def __init__(self):
        self.funds = 0  # cash on hand
        self.taxFund = 0  # taxes collected from current year (1/TAXFREQ's)
        self.roadFundEscrow = 0  # prepaid road maintenance (1/TAXFREQ's)
        self.roadFundEscrow = 0  # prepaid fire maintenance (1/TAXFREQ's)
        self.roadFundEscrow = 0  # prepaid police maintenance (1/TAXFREQ's)


'''
class History
structure to encapsulate census history
'''


class History(object):
    '''  '''

    def __init__(self):
        self.cityTime = 0
        self.res = [0 for x in xrange(0,240)]
        self.com = [0 for x in xrange(0,240)]
        self.ind = [0 for x in xrange(0,240)]
        self.money = [0 for x in xrange(0,240)]
        self.pollution = [0 for x in xrange(0,240)]
        self.crime = [0 for x in xrange(0,240)]
        self.resMax = 0
        self.comMax = 0
        self.indMax = 0


class B(object):
    '''
    behaviours
    '''
    FIRE = 0
    FLOOD = 1
    RADIOACTIVE = 2
    ROAD = 3
    RAIL = 4
    EXPLOSION = 5
    RESIDENTIAL = 6
    HOSPITAL_CHURCH = 7
    COMMERCIAL = 8
    INDUSTRIAL = 9
    COAL = 10
    NUCLEAR = 11
    FIRESTATION = 12
    POLICESTATION = 13
    STADIUM_EMPTY = 14
    STADIUM_FULL = 15
    AIRPORT = 16
    SEAPORT = 17


cityMessages = ConfigParser.ConfigParser()
cityMessages.read('res/citymessages.cfg')

'''
    class Engine
    city simulation engine
    
    Created new everytime a new or loaded city is created.
    
    instance data:
    map data
    census data
    history data
'''

class Engine(EventDispatcher):
    DEFAULT_WIDTH = 120
    DEFAULT_HEIGHT = 100

    def __init__(self, width=None, height=None):
        self.register_event_type("on_map_changed")
        self.register_event_type("on_evaluation_changed")
        self.register_event_type("on_date_changed")
        self.register_event_type("on_demand_changed")
        self.register_event_type("on_funds_changed")
        self.register_event_type("on_census_changed")
        self.register_event_type("on_power_indicator_changed")
        self.register_event_type("on_city_message")
        self.register_event_type("on_options_changed")
        self.register_event_type("on_city_sound")

        if width == None:
            width = self.DEFAULT_WIDTH
        if height == None:
            height = self.DEFAULT_HEIGHT
        ''' mapdata is stored as [column][row] '''
        self.map = create2dArray(height, width)
        self.updatedTiles = list()
        self.powerMap = create2dArray(self.getHeight(), self.getWidth(), False)
        self.noPowerIndicators = create2dArray(width, height, False)

        halfWidth = (width + 1) // 2
        halfHeight = (height + 1) // 2
        self.landValueMem = create2dArray(halfHeight, halfWidth, 0)
        self.pollutionMem = create2dArray(halfHeight, halfWidth, 0)
        self.crimeMem = create2dArray(halfHeight, halfWidth, 0)
        self.popDensity = create2dArray(halfHeight, halfWidth, 0)
        self.trfDensity = create2dArray(halfHeight, halfWidth, 0)

        quarterWidth = (width + 3) // 4
        quarterHeight = (height + 3) // 4
        self.terrainMem = create2dArray(quarterHeight, quarterWidth, 0)

        self.smWidth = (width + 7) // 8
        self.smHeight = (height + 7) // 8
        self.rateOGMem = create2dArray(self.smHeight, self.smWidth, 0)
        self.fireStMap = create2dArray(self.smHeight, self.smWidth, 0)
        self.policeMap = create2dArray(self.smHeight, self.smWidth, 0)
        self.policeMapEffect = create2dArray(self.smHeight, self.smWidth, 0)
        self.fireRate = create2dArray(self.smHeight, self.smWidth, 0)
        self.comRate = create2dArray(self.smHeight, self.smWidth, 0)

        self.centerMassX = halfWidth
        self.centerMassY = halfHeight

        ''' misc engine vars '''
        self.history = History()

        self.budget = CityBudget()
        self.budget.funds = 20000
        self.autoBulldoze = False
        self.autoBudget = False
        self.noDisasters = True

        self.newPower = False

        self.fCycle = 0  # counts simulation steps (mod 1024)
        self.sCycle = 0  # same as cityTime, except mod 1024
        self.aCycle = 0  # animation cycle (mod 960)

        self.cityTime = 0  # 1 week game time per "cityTime"
        self.totalPop = 0
        self.lastCityPop = 0

        self.pollutionMaxLocationX = 0
        self.pollutionMaxLocationY = 0

        self.needHospital = 0  # -1 too many already, 0 just right, 1 not enough
        self.needChurch = 0  # -1 too many already, 0 just right, 1 not enough

        self.crimeAverage = 0
        self.pollutionAverage = 0
        self.landValueAverage = 0
        self.trafficAverage = 0

        self.resValve = 0  # ranges between -2000 and 2000, updated by setValves
        self.comValve = 0  # ranges between -1500 and 1500
        self.indValve = 0  # same as comvalve
        self.resCap = False
        self.comCap = False
        self.indCap = False
        self.crimeRamp = 0
        self.polluteRamp = 0

        self.TAX_TABLE = [200,150,120,100,80,50,30,0,-10,-40,-100,
                          -150,-200,-250,-300,-350,-400,-450,-500,-550]

        self.cityTax = 7
        self.roadPercent = 1.0
        self.policePercent = 1.0
        self.firePrecent = 1.0

        self.taxEffect = 7
        self.roadEffect = 32
        self.policeEffect = 1000
        self.fireEffect = 1000

        self.cashFlow = 0


        self.VALVERATE = 2
        self.CENSUSRATE = 4
        self.TAXFREQ = 48

        self.gameLevel = 0

        self.clearCensus()
        self.initTileBehaviours()

    def cityMessage(self, category, stringOption):
        self.dispatch_event("on_city_message",
                            cityMessages.get(category,
                                             stringOption))

    def spend(self, amount):
        self.budget.funds -= amount
        self.dispatch_event("on_funds_changed", self.budget.funds)

    def testBounds(self, x, y):
        return (0 <= x < self.getWidth() and
                0 <= y < self.getHeight())

    def getWidth(self):
        return len(self.map[0])

    def getHeight(self):
        return len(self.map)

    def newCity(self):
        self.dispatch_event("on_funds_changed", self.budget.funds)
        self.dispatch_event('on_date_changed', self.cityTime)
        self.dispatch_event('on_census_changed', 0)

    def clearCensus(self):
        self.poweredZoneCount = 0
        self.unpoweredZoneCount = 0
        self.roadTotal = 0
        self.railTotal = 0
        self.resPop = 0
        self.comPop = 0
        self.indPop = 0
        self.resZoneCount = 0
        self.comZoneCount = 0
        self.indZoneCount = 0
        self.hospitalCount = 0
        self.churchCount = 0
        self.policeCount = 0
        self.fireStationCount = 0
        self.stadiumCount = 0
        self.firePop = 0
        self.coalCount = 0
        self.nuclearCount = 0
        self.seaportCount = 0
        self.airportCount = 0
        self.powerPlants = []

        self.fireStMap = create2dArray(self.smWidth, self.smHeight, 0)
        self.policeMap = create2dArray(self.smWidth, self.smHeight, 0)

    def saveCity(self, outFile):
        ''' saves the current city state to file '''
        pass

    def saveHistoryArray(self):
        pass

    def saveMisc(self):
        pass

    def saveMap(self):
        pass

    '''
        given a filename will load saved city data
    '''
    @classmethod
    def loadCity(cls, fileName):
        eng = cls()
        saveFile = open(fileName, "rb")
        try:
            cls.loadHistoryArray(saveFile, eng.history.res)
            cls.loadHistoryArray(saveFile, eng.history.com)
            cls.loadHistoryArray(saveFile, eng.history.ind)
            cls.loadHistoryArray(saveFile, eng.history.crime)
            cls.loadHistoryArray(saveFile, eng.history.pollution)
            cls.loadHistoryArray(saveFile, eng.history.money)
            speed = eng.loadMisc(saveFile)
            eng.loadMap(saveFile)
        except IOError as err:
            print(str(err))
            saveFile.close()
            return
        finally:
            saveFile.close()
        eng.checkPowerMap()
        eng.tileUpdateCheck()
        return speed, eng

    '''
        loads census history
    '''
    @staticmethod
    def loadHistoryArray(saveFile, array):
        for i in xrange(240):
            array.append(readShort(saveFile))

    '''
        loads misc city state
    '''

    def loadMisc(self, saveFile):
        readShort(saveFile)
        readShort(saveFile)
        self.resPop = readShort(saveFile)
        self.comPop = readShort(saveFile)
        self.indPop = readShort(saveFile)
        self.resValve = readShort(saveFile)
        self.comValve = readShort(saveFile)
        self.indValve = readShort(saveFile)
        self.cityTime = readInt(saveFile)
        self.crimeRamp = readShort(saveFile)
        self.polluteRamp = readShort(saveFile)
        self.landValueAverage = readShort(saveFile)
        self.crimeAverage = readShort(saveFile)
        self.pollutionAverage = readShort(saveFile)
        self.gameLevel = readShort(saveFile)
        readShort(saveFile)  # evaluation.cityClass
        readShort(saveFile)  # evaluation.cityScore

        for i in xrange(18, 50):
            readShort(saveFile)

        self.budget.funds = readInt(saveFile)  # budget.totalFunds

        self.autoBulldoze = readShort(saveFile) != 0  # autoBulldoze
        self.autoBudget = readShort(saveFile)  # autoBudget
        self.autoGo = readShort(saveFile)  # autoGo
        readShort(saveFile)  # userSoundOn
        self.cityTax = readShort(saveFile)  # cityTax
        self.taxEffect = self.cityTax
        simSpeedAsInt = readShort(saveFile)  # simSpeedAsInt
        ''' budget numbers '''
        n = readInt(saveFile)  # police
        self.policePercent = n / 65536.0
        n = readInt(saveFile)  # fire
        self.firePercent = n / 65536.0
        n = readInt(saveFile)  # road
        self.roadPercent = n / 65536.0

        for i in xrange(64, 120):
            readShort(saveFile)

        if self.cityTime < 0: self.cityTime = 0
        if self.cityTax < 0 or self.cityTax > 20:
            self.cityTax = 7
        if self.gameLevel < 0 or self.gameLevel > 2:
            self.gameLevel = 0

        self.resCap = False
        self.comCap = False
        self.indCap = False

        return simSpeedAsInt

    '''
        loads the tile values
    '''
    def loadMap(self, saveFile):
        for x in xrange(self.DEFAULT_WIDTH):
            for y in xrange(self.DEFAULT_HEIGHT):
                z = readShort(saveFile)
                # clear 6 most significant bits (leaving 10 lsb's)
                z &= ~(1024 | 2048 | 4096 | 8192 | 16384)
                self.map[y][x] = z
                self.updatedTiles.append((x, y, z))

    '''
        Will setup the power system in a newly loaded city save.
    '''

    def checkPowerMap(self):
        self.coalCount = 0
        self.nuclearCount = 0

        self.powerPlants = []
        for y in xrange(self.getHeight()):
            for x in xrange(self.getWidth()):
                tile = self.getTile(x, y)
                if tile == NUCLEAR:
                    self.nuclearCount += 1
                    self.powerPlants.append(CityLocation(x, y))
                elif tile == POWERPLANT:
                    self.coalCount += 1
                    self.powerPlants.append(CityLocation(x, y))

        self.powerScan()
        self.newPower = True

    def testChange(self):
        # fire test
        self.setTile(10, 10, FIRE)
        self.setTile(10, 12, 83)
        self.setTile(10, 14, 82)

    def getTile(self, x, y):
        return self.map[y][x] & LOMASK

    def getTileRaw(self, x, y):
        return self.map[y][x]

    def isTileDozeable(self, eff):
        myTile = eff.getTile(0, 0)
        ts = tiles.get(myTile)
        if ts.canBulldoze:
            return True

        if ts.owner is not None:
            baseTile = eff.getTile(-ts.ownerOffsetX, -ts.ownerOffsetY)
            return not ts.owner.tileNum == baseTile

        return False

    '''
        this method clears PWRBIT of given tile
    '''

    def setTile(self, x, y, newTile):
        if (newTile & LOMASK) == newTile:
            self.map[y][x] = newTile
            if (x, y, newTile) not in self.updatedTiles:
                self.updatedTiles.append((x, y, newTile))

    def setTilePower(self, x, y, power):
        if power:
            d = PWRBIT
        else:
            d = 0
        self.map[y][x] = self.map[y][x] & (~PWRBIT) | d

    def setValves(self):
        normResPop = self.resPop // 8
        self.totalPop = normResPop + self.comPop + self.indPop

        if normResPop != 0.0:
            employment = (self.history.com[1] + self.history.ind[1]) // normResPop
        else:
            employment = 1

        migration = normResPop * (employment - 1)
        BIRTH_RATE = 0.02
        births = normResPop * BIRTH_RATE
        projectedResPop = normResPop + migration + births

        temp = self.history.com[1] + self.history.ind[1]
        if temp != 0.0:
            laborBase = self.history.res[1] // temp
        else:
            laborBase = 1

        # clamp laborBase between -0.0 and 1.3
        laborBase = max(0.0, min(1.3, laborBase))

        internalMarket = normResPop + self.comPop + self.indPop
        projectedComPop = internalMarket * laborBase

        z = self.gameLevel
        if z == 0:
            temp = 1.2
        elif z == 1:
            temp = 1.1
        elif z == 2:
            temp = 0.98

        projectedIndPop = self.indPop * laborBase * temp
        if projectedIndPop < 5.0:
            projectedIndPop = 5.0

        if normResPop != 0:
            resRatio = projectedResPop // normResPop
        else:
            resRatio = 1.3

        if self.comPop != 0:
            comRatio = projectedComPop // self.comPop
        else:
            comRatio = projectedComPop

        if self.indPop != 0:
            indRatio = projectedIndPop // self.indPop
        else:
            indRatio = projectedIndPop

        if resRatio > 2.0:
            resRatio = 2.0
        if comRatio > 2.0:
            comRatio = 2.0
        if indRatio > 2.0:
            indRatio = 2.0

        z2 = self.taxEffect + self.gameLevel
        if z2 > 20:
            z2 = 20

        resRatio = (resRatio - 1) * 600 + self.TAX_TABLE[z2]
        comRatio = (comRatio - 1) * 600 + self.TAX_TABLE[z2]
        indRatio = (indRatio - 1) * 600 + self.TAX_TABLE[z2]

        self.resValve += int(resRatio)
        self.comValve += int(comRatio)
        self.indValve += int(indRatio)

        if self.resValve > 2000:
            self.resValve = 2000
        elif self.resValve < -2000:
            self.resValve = -2000

        if self.comValve > 1500:
            self.comValve = 1500
        elif self.comValve < -1500:
            self.comValve = -1500

        if self.indValve > 1500:
            self.indValve = 1500
        elif self.indValve < -1500:
            self.indValve = -1500

        if self.resCap and self.resValve > 0:
            # residents demand stadium
            self.resValve = 0

        if self.comCap and self.comValve > 0:
            # commerce deamds airport
            self.comValve = 0

        if self.indCap and self.indValve > 0:
            # industry demands seaport
            self.indValve = 0

        #print self.resValve,self.comValve,self.indValve

        self.dispatch_event('on_demand_changed')

    @staticmethod
    def smoothTerrain(qTem):
        QWX = len(qTem[0])
        QWY = len(qTem)

        mem = create2dArray(QWY, QWX, 0)
        for y in xrange(QWY):
            for x in xrange(QWX):
                z = 0
                if x > 0:
                    z += qTem[y][x-1]
                if x + 1 < QWX:
                    z += qTem[y][x+1]
                if y > 0:
                    z += qTem[y-1][x]
                if y + 1 < QWY:
                    z += qTem[y+1][x]
                mem[y][x] = z // 4 + qTem[y][x] // 2

        return mem

    def simulate(self, dt):
        self.fCycle = (self.fCycle + 1) % 1024
        mod16 = self.fCycle % 16

        band = self.getWidth() // 8
        if mod16 == 0:
            self.tileUpdateCheck()
            self.sCycle = (self.sCycle + 1) % 1024
            self.cityTime += 1
            self.dispatch_event('on_date_changed', self.cityTime)
            if self.sCycle % 2 == 0:
                self.setValves()
            self.clearCensus()
        elif mod16 == 1:
            self.mapScan(0 * band, 1 * band)
        elif mod16 == 2:
            self.mapScan(1 * band, 2 * band)
        elif mod16 == 3:
            self.mapScan(2 * band, 3 * band)
        elif mod16 == 4:
            self.mapScan(3 * band, 4 * band)
        elif mod16 == 5:
            self.mapScan(4 * band, 5 * band)
        elif mod16 == 6:
            self.mapScan(5 * band, 6 * band)
        elif mod16 == 7:
            self.mapScan(6 * band, 7 * band)
        elif mod16 == 8:
            self.mapScan(7 * band, self.getWidth())
        elif mod16 == 9:
            if self.cityTime % self.CENSUSRATE == 0:
                self.takeCensus()

                if self.cityTime % (self.CENSUSRATE * 12) == 0:
                    self.takeCensus2()

                self.dispatch_event("on_census_changed", self.lastCityPop)

            self.collectTaxPartial()

            if self.cityTime % self.TAXFREQ == 0:
                self.collectTax()
                #self.evaluation.cityEvaluation()

            '''print (self.history.res[0],self.history.res[1],self.history.res[2],
                   self.history.res[3],self.history.res[4],self.history.res[5])'''

        elif mod16 == 10:
            if self.sCycle % 5 == 0:
                self.decROGMem()
            self.decTrafficMem()
            # fire overlay changed events here
            self.doMessages()

        elif mod16 == 11:
            self.powerScan()
            self.newPower = True
        elif mod16 == 12:
            self.ptlScan()
        elif mod16 == 13:
            self.crimeScan()
        elif mod16 == 14:
            self.popDenScan()
        elif mod16 == 15:
            self.fireAnalysis()
            self.doDisasters()

        # should this be once a cycle?


        #TODO move objects here

    def computePopDen(self, x, y, tile):
        if tile == RESCLR:
            return self.doFreePop(x, y)
        if tile < COMBASE:
            return residentialZonePop(tile)
        if tile < INDBASE:
            return commercialZonePop(tile)
        if tile < PORTBASE:
            return industrialZonePop(tile)
        return 0

    @staticmethod
    def doSmooth(tem):
        h = len(tem)
        w = len(tem[0])
        tem2 = create2dArray(h, w, 0)

        for y in xrange(h):
            for x in xrange(w):
                z = tem[y][x]
                if x > 0:
                    z += tem[y][x-1]
                if x + 1 < w:
                    z += tem[y][x+1]
                if y > 0:
                    z += tem[y-1][x]
                if y + 1 < h:
                    z += tem[y+1][x]
                z /= 4
                if z > 255:
                    z = 255
                tem2[y][x] = z
        return tem2


    def doDisasters(self):
        pass

    def fireAnalysis(self):
        pass

    '''
        will move the given location a direction.
        respects map borders
        0=NORTH,1=EAST,2=SOUTH,3=WEST,4=skip
    '''

    def movePowerLocation(self, loc, dir):
        if dir == 0:
            if loc.y > 0:
                loc.y -= 1
                return True, loc
            else:
                return False, loc
        elif dir == 1:
            if loc.x + 1 < self.getWidth():
                loc.x += 1
                return True, loc
            else:
                return False, loc
        elif dir == 2:
            if loc.y + 1 < self.getHeight():
                loc.y += 1
                return True, loc
            else:
                return False, loc
        elif dir == 3:
            if loc.x > 0:
                loc.x -= 1
                return True, loc
            else:
                return False, loc
        elif dir == 4:
            return True, loc

        return False, loc

    '''
        called once a cycle. does the actual work of populating powermap
            starts at all powerplants and traces the power path.
    '''

    def powerScan(self):
        self.powerMap = create2dArray(self.getHeight(), self.getWidth(), False)

        maxPower = self.coalCount * 700 + self.nuclearCount * 2000
        numPower = 0

        while len(self.powerPlants) != 0:
            loc = self.powerPlants.pop()
            aDir = 4
            while True:
                numPower += 1
                if numPower > maxPower:
                    self.cityMessage("general", "BROWNOUTS_REPORT")
                    return
                r, loc = self.movePowerLocation(loc, aDir)
                self.powerMap[loc.y][loc.x] = True

                conNum = 0
                theDir = 0
                while theDir < 4 and conNum < 2:
                    ''' test for conductive tiles in direction(theDir) '''
                    xSave = loc.x
                    ySave = loc.y
                    rv = False
                    r, loc = self.movePowerLocation(loc, theDir)
                    if r:
                        t = self.getTile(loc.x, loc.y)
                        spec = tiles.get(t)
                        conducts =  spec is not None and spec.canConduct
                        rv = (
                            conducts and
                            t != NUCLEAR and
                            t != POWERPLANT and
                            not self.hasPower(loc.x, loc.y))
                    loc.x = xSave
                    loc.y = ySave
                    r = rv

                    if r:
                        conNum += 1
                        aDir = theDir
                    theDir += 1

                if conNum > 1:
                    self.powerPlants.append(CityLocation(loc.x, loc.y))
                if conNum == 0:
                    break

    def addTraffic(self, mapX, mapY, traffic):
        z = self.trfDensity[mapY//2][mapX//2]
        z += traffic

        # why is this randomly capped to 240? why not rest of time?
        if z > 240 and randint(0,5) == 0:
            z = 240
            self.trafficMaxLocationX = mapX
            self.trafficMaxLocationY = mapY

            # set helicopter desination here

        self.trfDensity[mapY//2][mapX//2] = z

    def decROGMem(self):
        pass

    def decTrafficMem(self):
        for y in xrange(0, len(self.trfDensity)):
            for x in xrange(0, len(self.trfDensity[y])):
                z = self.trfDensity[y][x]
                if z != 0:
                    if z > 200:
                        self.trfDensity[y][x] = z - 34
                    elif z > 24:
                        self.trfDensity[y][x] = z - 24
                    else:
                        self.trfDensity[y][x] = 0

    '''
        calculate manhatten distance (in 2-units) from center of city
        capped at 32
    '''
    def getDisCC(self, x, y):
        assert 0 <= x <= self.getWidth() // 2
        assert 0 <= y <= self.getHeight() // 2

        yDis = abs(y - self.centerMassY // 2)
        xDis = abs(x - self.centerMassX // 2)

        z = xDis + yDis
        if z > 32:
            return 32
        else:
            return z


    '''
        pollution, terrain and land-value
    '''
    def ptlScan(self):
        qX = (self.getWidth() + 3) // 4
        qY = (self.getHeight() + 3) // 4
        qTem = create2dArray(qY, qX, 0)

        landValueTotal = 0
        landValueCount = 0

        HWLDX = (self.getWidth() + 1) // 2
        HWLDY = (self.getHeight() + 1) // 2
        tem = create2dArray(HWLDY, HWLDX, 0)
        for x in xrange(HWLDX):
            for y in xrange(HWLDY):
                pLevel = 0
                lvFlag = 0
                zx = 2 * x
                zy = 2 * y

                for mx in xrange(zx, zx + 2):
                    for my in xrange(zy, zy + 2):
                        tile = self.getTile(mx, my)
                        if tile != DIRT:
                            if tile < RUBBLE:  # natural land features
                                qTem[y//2][x//2] += 15
                                continue
                            pLevel += getPollutionValue(tile)
                            if isConstructed(tile):
                                lvFlag += 1

                if pLevel < 0:
                    pLevel = 250

                if pLevel > 255:
                    pLevel = 255

                tem[y][x] = pLevel

                if lvFlag != 0:
                    # land value equation

                    dis = 34 - self.getDisCC(x, y)
                    dis *= 4
                    dis += self.terrainMem[y//2][x//2]
                    dis -= self.pollutionMem[y][x]
                    if self.crimeMem[y][x] > 190:
                        dis -= 20
                    if dis > 250:
                        dis = 250
                    if dis < 1:
                        dis = 1
                    self.landValueMem[y][x] = dis
                    landValueTotal += dis
                    landValueCount += 1
                else:
                    self.landValueMem[y][x] = 0

        if landValueCount != 0:
            self.landValueAverage = landValueTotal // landValueCount
        else:
            self.landValueAverage = 0

        tem = self.doSmooth(tem)
        tem = self.doSmooth(tem)

        pCount = 0
        pTotal = 0
        pMax = 0

        for x in xrange(HWLDX):
            for y in xrange(HWLDY):
                z = tem[y][x]
                self.pollutionMem[y][x] = z

                if z != 0:
                    pCount += 1
                    pTotal += z

                    if z > pMax or (z == pMax and randint(0, 3) == 0):
                        pMax = z
                        self.pollutionMaxLocationX = 2 * x
                        self.pollutionMaxLocationY = 2 * y

        if pCount != 0:
            self.pollutionAverage = pTotal // pCount
        else:
            self.pollutionAverage = 0

        self.terrainMem = self.smoothTerrain(qTem)

        # fire map overlay changed events


    '''

    '''
    def crimeScan(self):
        pass

    '''

    '''
    def popDenScan(self):

        xTot = 0
        yTot = 0
        zoneCount = 0
        width = self.getWidth()
        height = self.getHeight()
        tem = create2dArray((height + 1) // 2, (width + 1) // 2)

        for x in xrange(width):
            for y in xrange(height):
                tile = self.getTile(x, y)
                if isZoneCenter(tile):
                    den = self.computePopDen(x, y, tile) * 8
                    #print "density: " + str(den)
                    if den > 254:
                        den = 254
                    tem[y//2][x//2] = den
                    xTot += x
                    yTot += y
                    zoneCount += 1

        '''print "--------------------------------"
        print "before"
        print tem'''

        tem = self.doSmooth(tem)
        tem = self.doSmooth(tem)
        tem = self.doSmooth(tem)

        '''print "--------------------------------"
        print "after"
        print tem'''

        for x in xrange((width + 1) // 2):
            for y in xrange((height + 1) // 2):
                #print x,y,2*tem[y][x]
                self.popDensity[y][x] = 2 * tem[y][x]
                #print self.popDensity[y][x]

        self.distIntMarket()

        if zoneCount != 0:
            self.centerMassX = xTot // zoneCount
            self.centerMassY = yTot // zoneCount
        else:
            self.centerMassX = (width + 1) // 2
            self.centerMassY = (height + 1) // 2

        # fire appropriate map overlay events



    def distIntMarket(self):
        for y in xrange(len(self.comRate)):
            for x in xrange(len(self.comRate[y])):
                z = self.getDisCC(x * 4, y * 4)
                z //= 4
                z = 64 - z
                self.comRate[y][x] = z


    def smoothFirePoliceMap(self, oMap):
        pass

    '''
        checks powerbit of tile value ()
    '''

    def isTilePowered(self, xpos, ypos):

        return (self.getTileRaw(xpos, ypos) & PWRBIT) == PWRBIT

    '''
        checks powermap

    '''

    def hasPower(self, x, y):
        return self.powerMap[y][x]

    '''
        fires an on_map_changed event if there are dirty tiles
    '''

    def tileUpdateCheck(self):
        if len(self.updatedTiles) != 0:
            self.dispatch_event("on_map_changed", self.updatedTiles)
            self.updatedTiles = list()

    '''
        tile behaviours allow an action to be processed for every tile
    '''

    def initTileBehaviours(self):
        bb = dict()

        bb["FIRE"] = TerrainBehaviour(self, B.FIRE)
        bb["FLOOD"] = TerrainBehaviour(self, B.FLOOD)
        bb["RADIOACTIVE"] = TerrainBehaviour(self, B.RADIOACTIVE)
        bb["ROAD"] = TerrainBehaviour(self, B.ROAD)
        bb["RAIL"] = TerrainBehaviour(self, B.RAIL)
        bb["EXPLOSION"] = TerrainBehaviour(self, B.EXPLOSION)
        bb["RESIDENTIAL"] = MapScanner(self, B.RESIDENTIAL)
        bb["HOSPITAL_CHURCH"] = MapScanner(self, B.HOSPITAL_CHURCH)
        bb["COMMERCIAL"] = MapScanner(self, B.COMMERCIAL)
        bb["INDUSTRIAL"] = MapScanner(self, B.INDUSTRIAL)
        bb["COAL"] = MapScanner(self, B.COAL)
        bb["NUCLEAR"] = MapScanner(self, B.NUCLEAR)
        bb["FIRESTATION"] = MapScanner(self, B.FIRESTATION)
        bb["POLICESTATION"] = MapScanner(self, B.POLICESTATION)
        bb["STADIUM_EMPTY"] = MapScanner(self, B.STADIUM_EMPTY)
        bb["STADIUM_FULL"] = MapScanner(self, B.STADIUM_FULL)
        bb["AIRPORT"] = MapScanner(self, B.AIRPORT)
        bb["SEAPORT"] = MapScanner(self, B.SEAPORT)

        self.tileBehaviours = bb

    '''
        iterates over a section of map, invoking their process fcn
    '''
    def mapScan(self, x0, x1):
        #print((x0,x1))
        for x in xrange(x0, x1):
            for y in xrange(0, self.getHeight()):
                tile = self.map[y][x] & LOMASK
                behaviourString = tiles.get(tile).getAttribute("behavior")
                if behaviourString is None:
                    continue
                b = self.tileBehaviours[behaviourString]
                if b is not None:
                    b.processTile(x, y)
                else:
                    assert False

    def setTilePowerIndicator(self, x, y, value):
        if not self.noPowerIndicators[x][y] and value:
            self.noPowerIndicators[x][y] = True
            self.dispatch_event("on_power_indicator_changed", (x, y, True))
        elif self.noPowerIndicators[x][y] and not value:
            self.noPowerIndicators[x][y] = False
            self.dispatch_event("on_power_indicator_changed", (x, y, False))

    def getTileIndicator(self, x, y):
        return self.noPowerIndicators[x][y]

    '''
        Counts the population in a certain type of residential zone
    '''
    def doFreePop(self, xPos, yPos):
        count = 0
        #print "do free pop"
        for x in xrange(xPos - 1, xPos + 2):
            for y in xrange(yPos - 1, yPos + 2):
                if self.testBounds(x, y):
                    loc = self.getTile(x, y)
                    if LHTHR <= loc <= HHTHR:
                        #print count
                        count += 1
        #print "final: " + str(count)
        return count

    def toggleAutoBudget(self):
        self.autoBudget = not self.autoBudget
        self.dispatch_event("on_options_changed")

    def toggleAutoBulldoze(self):
        self.autoBulldoze = not self.autoBulldoze
        self.dispatch_event("on_options_changed")

    def toggleDisasters(self):
        self.noDisasters = not self.noDisasters
        self.dispatch_event("on_options_changed")


    def killZone(self, xPos, yPos, zoneTile):
        pass

    '''
        sets all tiles for a zone to a powered state
    '''

    def powerZone(self, xPos, yPos, zoneSize):
        assert zoneSize.chkMinSize(3)

        for dx in xrange(zoneSize.width):
            for dy in xrange(zoneSize.height):
                x = xPos - 1 + dx
                y = yPos - 1 + dy
                tile = self.getTileRaw(x, y)
                ts = tiles.get(tile & LOMASK)
                if ts is not None and ts.onPower is not None:
                    # print "onPower: " + str((x,y,ts.onPower.tileNum))
                    self.setTile(x, y,
                                 ts.onPower.tileNum or tile & ALLBITS)

    '''
        sets all tiles for a zone to a unpowered state
    '''

    def shutdownZone(self, xPos, yPos, zoneSize):
        assert zoneSize.chkMinSize(3)

        for dx in xrange(zoneSize.width):
            for dy in xrange(zoneSize.height):
                x = xPos - 1 + dx
                y = yPos - 1 + dy
                tile = self.getTileRaw(x, y)
                ts = tiles.get(tile & LOMASK)
                if ts is not None and ts.onShutdown is not None:
                    self.setTile(x, y,
                                 ts.onShutdown.tileNum or tile & ALLBITS)

    def takeCensus(self):
        resMax = 0
        comMax = 0
        indMax = 0

        for i in xrange(118, -1, -1):
            if self.history.res[i] > resMax:
                resMax = self.history.res[i]
            if self.history.com[i] > comMax:
                comMax = self.history.com[i]
            if self.history.ind[i] > indMax:
                indMax = self.history.ind[i]

            self.history.res[i + 1] = self.history.res[i]
            self.history.com[i + 1] = self.history.com[i]
            self.history.ind[i + 1] = self.history.ind[i]
            self.history.crime[i + 1] = self.history.crime[i]
            self.history.pollution[i + 1] = self.history.pollution[i]
            self.history.money[i + 1] = self.history.money[i]

        self.history.resMax = resMax
        self.history.comMax = comMax
        self.history.indMax = indMax

        #print "RESPOP: " + str(self.resPop)
        self.history.res[0] = self.resPop // 8
        self.history.com[0] = self.comPop
        self.history.ind[0] = self.indPop

        self.crimeRamp += (self.crimeAverage - self.crimeRamp) // 4
        self.history.crime[0] = min(255, self.crimeRamp)

        self.polluteRamp += (self.pollutionAverage - self.polluteRamp) // 4
        self.history.pollution[0] = min(255, self.polluteRamp)

        moneyScaled = self.cashFlow // 20 + 128
        if moneyScaled < 0:
            moneyScaled = 0
        if moneyScaled > 255:
            moneyScaled = 255
        self.history.money[0] = moneyScaled

        self.history.cityTime = self.cityTime

        if self.hospitalCount < self.resPop // 256.:
            self.needHospital = 1
        elif self.hospitalCount > self.resPop // 256.:
            self.needHospital = -1
        else:
            self.needHospital = 0

        if self.churchCount < self.resPop // 256.:
            self.needChurch = 1
        elif self.churchCount > self.resPop // 256.:
            self.needChurch = -1
        else:
            self.needChurch = 0

    def takeCensus2(self):
        resMax = 0
        comMax = 0
        indMax = 0

        for i in xrange(238, 119, -1):
            if self.history.res[i] > resMax:
                resMax = self.history.res[i]
            if self.history.com[i] > comMax:
                comMax = self.history.com[i]
            if self.history.ind[i] > indMax:
                indMax = self.history.ind[i]

            self.history.res[i + 1] = self.history.res[i]
            self.history.com[i + 1] = self.history.com[i]
            self.history.ind[i + 1] = self.history.ind[i]
            self.history.crime[i + 1] = self.history.crime[i]
            self.history.pollution[i + 1] = self.history.pollution[i]
            self.history.money[i + 1] = self.history.money[i]

        self.history.res[120] = self.resPop // 8.
        self.history.com[120] = self.comPop
        self.history.ind[120] = self.indPop
        self.history.crime[120] = self.history.crime[0]
        self.history.pollution[120] = self.history.pollution[0]
        self.history.money[120] = self.history.money[0]

    def collectTaxPartial(self):
        return

        self.lastRoadTotal = self.roadTotal
        self.lastRailTotal = self.railTotal
        self.lastTotalPop = self.totalPop
        self.lastFireStationCount = self.fireStationCount
        self.lastPoliceCount = self.policeCount

        b = self.generateBudget()

        self.budget.taxFund += b.taxIncome
        self.budget.roadFundEscrow -= b.roadFunded
        self.budget.fireFundEscrow -= b.fireFunded
        self.budget.policeFundEscrow -= b.policeFund

        self.taxEffect = b.taxRate
        #self.roadEffect = b.roadRequest != 0



    def collectTax(self):
        pass

    def generateBudget(self):
        pass

    def getPopulationDensity(self, xPos, yPos):
        return self.popDensity[yPos // 2][xPos // 2]

    def checkGrowth(self):
        if self.cityTime % 4 == 0:
            newPop = (self.resPop + self.comPop * 8 + self.indPop * 8) * 20

            self.lastCityPop = newPop

    def doMessages(self):

        self.checkGrowth()

        totalZoneCount = self.resZoneCount + self.comZoneCount + self.indZoneCount
        powerCount = self.nuclearCount + self.coalCount

        z = self.cityTime % 64
        if z == 0 and totalZoneCount // 4 >= self.resZoneCount:
            self.dispatch_event("on_city_message", MicropylisMessage.NEED_RES)
        elif z == 5 and totalZoneCount // 8 >= self.comZoneCount:
            self.dispatch_event("on_city_message", MicropylisMessage.NEED_COM)
        elif z == 10 and totalZoneCount // 8 >= self.indZoneCount:
            self.dispatch_event("on_city_message", MicropylisMessage.NEED_IND)
        elif z == 14 and 10 < totalZoneCount and totalZoneCount * 2 > self.roadTotal:
            self.dispatch_event("on_city_message", MicropylisMessage.NEED_ROADS)
        #elif z == 18 and
        elif z == 26:
            self.resCap = self.resPop > 500 and self.stadiumCount == 0
            if self.resCap:
                self.dispatch_event("on_city_message", MicropylisMessage.NEED_STADIUM)
        elif z == 28:
            self.indCap = self.indPop > 500 and self.seaportCount == 0
            if self.indCap:
                self.dispatch_event("on_city_message", MicropylisMessage.NEED_SEAPORT)
        elif z == 30:
            self.comCap = self.comPop > 500 and self.airportCount == 0
            if self.comCap:
                self.dispatch_event("on_city_message", MicropylisMessage.NEED_AIRPORT)

    def queryZoneStatus(self, xPos, yPos):
        pass

    def getLandValue(self, xPos, yPos):
        if self.testBounds(xPos, yPos):
            return self.landValueMem[yPos//2][xPos//2]
        else:
            return 0

    def getTrafficDensity(self, xPos, yPos):
        if self.testBounds(xPos, yPos):
            #print str(xPos) + " " + str(yPos) + " " + str(self.trfDensity[yPos/2][xPos/2])
            return self.trfDensity[yPos//2][xPos//2]
        else:
            return 0

    def setGameLevel(self, newLevel):
        assert gameLevel.isValid(newLevel)

        self.gameLevel = newLevel

    def setFunds(self, totalFunds):
        self.budget.funds = totalFunds

    def getFunds(self):
        return self.budget.funds

    def getCensus(self):
        return self.totalPop

    def getCityTime(self):
        return self.cityTime

    def makeSound(self, soundTuple):
        self.dispatch_event("on_city_sound", soundTuple)
