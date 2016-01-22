'''
    main engine module
    
'''
import ConfigParser
import pyglet
from array import *
from engine.tileConstants import *
from util import readShort, readInt, create2dArray
from engine.terrainBehaviour import TerrainBehaviour
from mapScanner import MapScanner
from cityLocation import CityLocation


class CityBudget(object):
    def __init__(self):
        self.funds = 0 # cash on hand
        self.taxFund = 0 # taxes collected from current year (1/TAXFREQ's)
        self.roadFundEscrow = 0 # prepaid road maintenance (1/TAXFREQ's)
        self.roadFundEscrow = 0 # prepaid fire maintenance (1/TAXFREQ's)
        self.roadFundEscrow = 0 # prepaid police maintenance (1/TAXFREQ's)

'''
class History
structure to encapsulate census history
'''
class History(object):
    '''  '''
    def __init__(self):
        self.cityTime = 0
        self.res = array('H')
        self.com = array('H')
        self.ind = array('H')
        self.money = array('H')
        self.pollution = array('H')
        self.crime = array('H')
        self.resMax = 0
        self.comMax = 0
        self.indMax = 0
        
class B(object):
    '''
    behaviours
    '''
    FIRE=0
    FLOOD=1
    RADIOACTIVE=2
    ROAD=3
    RAIL=4
    EXPLOSION=5
    RESIDENTIAL=6
    HOSPITAL_CHURCH=7
    COMMERCIAL=8
    INDUSTRIAL=9
    COAL=10
    NUCLEAR=11
    FIRESTATION=12
    POLICESTATION=13
    STADIUM_EMPTY=14
    STADIUM_FULL=15
    AIRPORT=16
    SEAPORT=17
    
    
    
cityMessages = ConfigParser.ConfigParser()
cityMessages.read('res/citymessages.cfg')    


'''
    class Engine
    city simulation engine
    
    instance data:
    map data
    census data
    history data
'''
class Engine(pyglet.event.EventDispatcher):
    DEFAULT_WIDTH = 120
    DEFAULT_HEIGHT = 100
    
    def __init__(self, width=None, height=None):
        self.register_event_type("on_map_changed")
        self.register_event_type("on_funds_changed")
        self.register_event_type("on_census_changed")
        self.register_event_type("on_power_indicator_changed")
        self.register_event_type("city_message")
        
        self.initTileBehaviours()
        
        self.canAutoBulldoze = True

        self.newCity(width, height)

        
    def cityMessage(self, category, stringOption):
            self.dispatch_event("city_message", 
                                cityMessages.get(category,
                                                 stringOption))
        
    def spend(self, amount):
        self.budget.funds -= amount
        self.dispatch_event("on_funds_changed")
    
    def testBounds(self, x, y):
        return x >= 0 and x < self.getWidth()\
            and y >= 0 and y < self.getHeight()
        
    def getWidth(self):
        return len(self.map[0])
    
    def getHeight(self):
        return len(self.map)
        
    def newCity(self, width=None, height=None):
        ''' mapdata is stored as [column][row] '''
        if (width == None):
            width = self.DEFAULT_WIDTH
        if (height == None):
            height = self.DEFAULT_HEIGHT
        self.map = create2dArray(height, width)
        self.updatedTiles = list()
        
        self.powerMap = create2dArray(height, width, False)
        self.noPowerIndicators = create2dArray(width, height, False)
        
        ''' misc engine vars '''
        self.history = History()
        self.budget = CityBudget()
        self.budget.funds = 20000
        
        self.fCycle = 0 # counts simulation steps (mod 1024)
        self.sCycle = 0 # same as cityTime, except mod 1024
        self.aCycle = 0 # animation cycle (mod 960)
        
        self.cityTime = 0 # 1 week game time per "cityTime"
        
        self.clearCensus()
        

        
    def clearCensus(self):
        '''  '''
        self.poweredZoneCount = 0
        self.unpoweredZoneCount = 0
        self.roadTotal = 0
        self.roadEffect = 0
        self.firePop = 0
        self.coalCount = 0
        self.nuclearCount = 0
        self.powerPlants = []
        
    
    def saveCity(self, outFile):
        ''' saves the current city state to file '''
        pass

    def saveHistoryArray(self):
        pass

    def saveMisc(self):
        pass
    
    def saveMap(self):
        pass
    

    ''' given a filename will load saved city data '''
    def loadCity(self, fileName):
        saveFile = open(fileName, "rb")
        try:
            self.loadHistoryArray(saveFile, self.history.res)
            self.loadHistoryArray(saveFile, self.history.com)
            self.loadHistoryArray(saveFile, self.history.ind)
            self.loadHistoryArray(saveFile, self.history.crime)
            self.loadHistoryArray(saveFile, self.history.pollution)
            self.loadHistoryArray(saveFile, self.history.money)
            self.loadMisc(saveFile)
            self.loadMap(saveFile)
        except IOError as err:
            print str(err)
        finally:
            saveFile.close()
            #self.checkPowerMap()
            self.dispatch_event("on_map_changed", self.updatedTiles)
            self.dispatch_event("on_funds_changed")
    
    
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
    
    def loadHistoryArray(self, saveFile, array):
        '''  '''
        for i in xrange(240):
            array.append(readShort(saveFile))
        
    def loadMisc(self, saveFile):
        '''  '''
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
        readShort(saveFile) #evaluation.cityClass
        readShort(saveFile) #evaluation.cityScore
        
        for i in xrange(18,50):
            readShort(saveFile)
            
        self.budget.funds = readInt(saveFile) # budget.totalFunds
        
        self.budget.funds = 10000
        
        readShort(saveFile) # autoBulldoze
        readShort(saveFile) # autoBudget
        readShort(saveFile) # autoGo
        readShort(saveFile) # userSoundOn
        readShort(saveFile) # cityTax
        readShort(saveFile) # simSpeedAsInt
        ''' budget numbers '''
        readInt(saveFile) # police
        readInt(saveFile) # fire
        readInt(saveFile) # road
        
        for i in xrange(64,120):
            readShort(saveFile)
            
    def loadMap(self, saveFile):
        '''  '''
        for x in xrange(self.DEFAULT_WIDTH):
            for y in xrange(self.DEFAULT_HEIGHT):
                z = readShort(saveFile)
                # clear 6 most significant bits (leaving 10 lsb's)
                z &= ~(1024 | 2048 | 4096 | 8192 | 16384)
                self.map[y][x] = z
                self.updatedTiles.append((x,y))
                
    def testChange(self):
        # fire test
        self.setTile(10,10,FIRE)
        self.setTile(10,12,83)
        self.setTile(10,14,82)
        
    def getTile(self, x, y):
        '''  '''
        return self.map[y][x] & LOMASK
    
    def getTileRaw(self, x, y):
        '''  '''
        return self.map[y][x]
    
    ''' this method clears PWRBIT of given tile '''
    def setTile(self, x, y, newTile):
        if ((newTile & LOMASK) == newTile and \
                self.map[y][x] != newTile):
            self.map[y][x] = newTile
            self.updatedTiles.append((x,y))
            
    def setTilePower(self, x, y, power):
        '''  '''
        #print "MAP: " + str(self.map[y][x])
        if power:
            d = PWRBIT
        else:
            d = 0
        self.map[y][x] = self.map[y][x] & (~PWRBIT) | d
        #print "MAP: " + str(self.map[y][x])
    
    def setValves(self):
        '''  '''
        
        
        
        
        
        pass
        
        
        
    
    def animate(self, dt):
        '''  '''
        self.step()
        #self.moveObjects()
    
    def step(self):
        '''  '''
        self.fCycle = (self.fCycle + 1) % 1024
        self.simulate(self.fCycle % 16)
    
    
    def simulate(self, mod16):
        '''  '''
        band = self.getWidth() / 8
        #print "simulate " + str(mod16)
        if mod16 == 0:
            #print "bah"
            self.sCycle = (self.sCycle + 1) % 1024
            self.cityTime += 1
            if self.sCycle % 2 == 0:
                self.setValves()
            self.clearCensus()
        elif mod16 == 1:
            self.mapScan(0*band, 1*band)
        elif mod16 == 2:
            self.mapScan(1*band, 2*band)
        elif mod16 == 3:
            self.mapScan(2*band, 3*band)
        elif mod16 == 4:
            self.mapScan(3*band, 4*band)
        elif mod16 == 5:
            self.mapScan(4*band, 5*band)
        elif mod16 == 6:
            self.mapScan(5*band, 6*band)
        elif mod16 == 7:
            self.mapScan(6*band, 7*band)
        elif mod16 == 8:
            self.mapScan(7*band, self.getWidth())
        elif mod16 == 9:
            pass
        elif mod16 == 10:
            pass
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
            pass
        
        # should this be once a cycle?
        self.tileUpdateCheck()

    def testForConductive(self, loc, dir):
        ''' returns power condition of a location in a paticular direction'''
        xSave = loc.x
        ySave = loc.y
        
        rv = False
        
        r,loc = self.movePowerLocation(loc, dir)
        if r:
            t = self.getTile(loc.x, loc.y)
            rv = (
                  isConductive(t) and
                  t != NUCLEAR and
                  t != POWERPLANT and
                  not self.hasPower(loc.x, loc.y))
        loc.x = xSave
        loc.y = ySave
        return rv,loc
    
    
    def movePowerLocation(self, loc, dir):
        ''' 
            will move the given location a direction.
            respects map borders
            0=NORTH,1=EAST,2=SOUTH,3=WEST,4=skip
        '''
        if dir == 0:
            if loc.y > 0:
                loc.y -= 1
                return True,loc
            else:
                return False,loc
        elif dir == 1:
            if loc.x + 1 < self.getWidth():
                loc.x += 1
                return True,loc
            else:
                return False,loc
        elif dir == 2:
            if loc.y + 1 < self.getHeight():
                loc.y += 1
                return True,loc
            else:
                return False,loc
        elif dir == 3:
            if loc.x > 0:
                loc.x -= 1
                return True,loc
            else:
                return False,loc
        elif dir == 4:
            return True,loc
        
        return False,loc
            

    
    def powerScan(self):
        ''' called once a cycle. does the actual work of populating powermap 
            starts at all powerplants and traces the power path'''
        self.powerMap = create2dArray(self.getHeight(), self.getWidth(), False)
        
        maxPower = self.coalCount * 700 + self.nuclearCount * 2000
        numPower = 0
        
        while(len(self.powerPlants) != 0):
            loc = self.powerPlants.pop()
            aDir = 4
            conNum = 0
            while True:
                numPower += 1
                if numPower > maxPower:
                    self.cityMessage("general", "BROWNOUTS_REPORT")
                    return
                r,loc = self.movePowerLocation(loc, aDir)
                self.powerMap[loc.y][loc.x] = True
                
                conNum = 0
                theDir = 0
                while theDir < 4 and conNum < 2:
                    r,loc = self.testForConductive(loc, theDir)
                    if r:
                        conNum += 1
                        aDir = theDir
                    theDir += 1
                if conNum > 1:
                    self.powerPlants.append(CityLocation(loc.x, loc.y))
                if conNum == 0:
                    break
        
    
    def ptlScan(self):
        ''' pollution, terrain and land-value '''
        pass
    
    def crimeScan(self):
        '''  '''
        pass
    
    def popDenScan(self):
        '''  '''
        xTot = 0
        yTot = 0
        zoneCount = 0
        width = self.getWidth()
        height = self.getHeight()
        tem = create2dArray((height+1)/2, (width+1)/2)
        
        for x in xrange((width+1)/2):
            pass
        
        
        
    
    def isTilePowered(self, xpos, ypos):
        ''' checks powerbit of tile value () '''
        return (self.getTileRaw(xpos, ypos) & PWRBIT) == PWRBIT
    
    def hasPower(self, x, y):
        ''' checks powermap '''
        return self.powerMap[y][x]
    
        
    def tileUpdateCheck(self):
        ''' fires an on_map_changed event if their are dirty tiles'''
        if (len(self.updatedTiles) != 0):
            self.dispatch_event("on_map_changed", self.updatedTiles)
            self.updatedTiles = list()
            
    def initTileBehaviours(self):
        ''' tile behaviours allow an action to be processed for every tile '''
        
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
    
    def mapScan(self, x0, x1):
        ''' iterates over a section of map, invoking their process fcn'''
        for x in xrange(x0,x1):
            for y in xrange(0, self.getHeight()):
                tile = self.getTile(x,y)
                behaviourString = getTileBehaviour(tile)
                if behaviourString is None:
                    continue
                b = self.tileBehaviours[behaviourString]
                if b is not None:
                    b.processTile(x,y)
                else:
                    assert False
                    
    def setTileIndicator(self, x, y, value):
        if not self.noPowerIndicators[x][y] and value:
            self.noPowerIndicators[x][y] = True
            self.dispatch_event("on_power_indicator_changed",(x,y))
        elif self.noPowerIndicators[x][y] and not value:
            self.noPowerIndicators[x][y] = False
            self.dispatch_event("on_power_indicator_changed",(x,y))
    
    def getTileIndicator(self, x, y):
        return self.noPowerIndicators[x][y]
                    
                    
    def powerZone(self, xPos, yPos, zoneSize):
        '''
            sets all tiles for a zone to a powered state
        '''
        
        assert zoneSize >= 3
        assert zoneSize >= 3
        
        for dx in xrange(zoneSize.width):
            for dy in xrange(zoneSize.height):
                x = xPos - 1 + dx
                y = yPos - 1 + dy
                tile = self.getTileRaw(x, y)
                ts = Tiles().get(tile & LOMASK)
                if ts is not None and ts.onPower is not None:
                    #print "onPower: " + str((x,y,ts.onPower.tileNum))
                    self.setTile(x, y,
                                 ts.onPower.tileNum or tile & ALLBITS)
                           
        
    def shutdownZone(self, xPos, yPos, zoneSize):
        '''
            sets all tiles for a zone to a unpowered state
        '''
        assert zoneSize >= 3
        assert zoneSize >= 3
        
        for dx in xrange(zoneSize.width):
            for dy in xrange(zoneSize.height):
                x = xPos - 1 + dx
                y = yPos - 1 + dy
                tile = self.getTileRaw(x, y)
                ts = Tiles().get(tile & LOMASK)
                if ts is not None and ts.onShutdown is not None:
                    self.setTile(x, y,
                                 ts.onShutdown.tileNum or tile & ALLBITS)
        
    def takeCensus(self):
        pass    
        
        
        
        
        
        
        
        
    
    
    
    