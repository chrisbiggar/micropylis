'''
    main engine module
    
'''
import pyglet
from array import *
from engine.tileConstants import *
from engine.misc import *


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
        ''' mapdata is stored as [column][row] '''
        if (width == None):
            width = self.DEFAULT_WIDTH
        if (height == None):
            height = self.DEFAULT_HEIGHT
        self.map = create2dArray(height, width)
        self.history = History()
        self.register_event_type("on_map_changed")
        self.updatedTiles = list()
        
    def getTile(self, x, y):
        return self.map[y][x] & LOMASK
        
    def getWidth(self):
        return len(self.map[0])
    
    def getHeight(self):
        return len(self.map)
        
    def newCity(self):
        pass
    
    def clearCensus(self):
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
        pass
    
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
    
    def animate(self):
        self.step()
    
    def step(self):
        self.simulate(0)
            
    def simulate(self, mod16):
        
        if (len(self.updatedTiles) != 0):
            self.dispatch_event("on_map_changed", self.updatedTiles)
            self.updatedTiles = list()
    
    
    
    
    
    
    
    
    