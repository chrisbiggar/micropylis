'''
    main engine module
    
'''
import pyglet
from array import *
from engine.tileConstants import *
from util import readShort, readInt, create2dArray
from engine.terrainBehaviour import TerrainBehaviour


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
        
        ''' mapdata is stored as [column][row] '''
        if (width == None):
            width = self.DEFAULT_WIDTH
        if (height == None):
            height = self.DEFAULT_HEIGHT
        self.map = create2dArray(height, width)
        self.updatedTiles = list()
        
        ''' misc engine vars '''
        self.history = History()
        self.budget = CityBudget()
        self.budget.funds = 10000
        
        self.fCycle = 0 # counts simulation steps (mod 1024)
        self.sCycle = 0 # same as cityTime, except mod 1024
        self.aCycle = 0 # animation cycle (mod 960)
        
    def spend(self, amount):
        self.budget.funds -= amount
        self.dispatch_event("on_funds_changed")
        
    def getTile(self, x, y):
        return self.map[y][x] & LOMASK
    
    def testBounds(self, x, y):
        return x >= 0 and x < self.getWidth()\
            and y >= 0 and y < self.getHeight()
        
    def getWidth(self):
        return len(self.map[0])
    
    def getHeight(self):
        return len(self.map)
        
    def newCity(self):
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
            self.dispatch_event("on_map_changed", self.updatedTiles)
    
    def loadHistoryArray(self, saveFile, array):
        for i in range(240):
            array.append(readShort(saveFile))
        
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
        readShort(saveFile) #evaluation.cityClass
        readShort(saveFile) #evaluation.cityScore
        
        for i in range(18,50):
            readShort(saveFile)
            
        readInt(saveFile) # budget.totalFunds
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
        
        for i in range(64,120):
            readShort(saveFile)
            
    def loadMap(self, saveFile):
        for x in range(self.DEFAULT_WIDTH):
            for y in range(self.DEFAULT_HEIGHT):
                z = readShort(saveFile)
                # clear 6 most significant bits (leaving 10 lsb's)
                z &= ~(1024 | 2048 | 4096 | 8192 | 16384)
                self.map[y][x] = z
                self.updatedTiles.append((x,y))
                
    def testChange(self):
        for x in range(90):
            self.setTile(x,2,12+x)
            self.setTile(x,3,12+x)
            self.setTile(x,4,12+x)
            self.setTile(x,5,12+x)
    
    ''' this method clears PWRBIT of given tile '''
    def setTile(self, x, y, newTile):
        if ((newTile & LOMASK) == newTile and \
                self.map[y][x] != newTile):
            self.map[y][x] = newTile
            self.updatedTiles.append((x,y))
            
    def clearCensus(self):
        pass
    
    def setValves(self):
        pass
    
    def animate(self):
        self.aCycle = (self.aCycle + 1) % 960
        if self.aCycle % 2 == 0:
            self.step()
        #self.moveObjects()
        #self.animateTiles()
    
    def step(self):
        self.fCycle = (self.fCycle + 1) % 1024
        self.simulate(self.fCycle % 16)
            
    def simulate(self, mod16):
        band = self.getWidth() / 8
        
        if mod16 == 0:
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
            self.mapScan(7*band, 8*band)
        
        
        
        if (len(self.updatedTiles) != 0):
            self.dispatch_event("on_map_changed", self.updatedTiles)
            self.updatedTiles = list()
            
    def initTileBehaviours(self):
        bb = dict()
        
        bb["FIRE"] = TerrainBehaviour(self, B.FIRE)
        bb["FLOOD"] = TerrainBehaviour(self, B.FLOOD)
        #bb[]
        
        self.tileBehaviours = bb
    
    def mapScan(self, x0, x1):
        for x in range(x0,x1):
            for y in range(0, self.getHeight()):
                tile = self.getTile(x,y)
                behaviourString = getTileBehaviour(tile)
                if behaviourString is None:
                    return
                b = self.tileBehaviours[behaviourString]
                if b is not None:
                    b.processTile(x,y)
                else:
                    # raise error
                    pass
    
    
    
    