'''
Created on Oct 19, 2015

@author: chris
'''
from util.properties import Properties
from tilespec import BuildingInfo, TileSpec, parseTileSpec, generateTilenames

class Tiles(object):
    '''
        Uses Borg pattern for singleton behaviour.
    '''
    __shared_state = {}
    
    def __init__(self):
        self.__dict__ = self.__shared_state
    
    def getByName(self, name):
        return self._tilesByName[name]
    
    def get(self, num):
        if (num >=0 and num < len(self._tiles)):
            return self._tiles[num]
        else:
            return None
    
    def readTilesSpec(self, tilesSpecFile):
        tilesRc = Properties()
        tilesRc.load(open(tilesSpecFile))
        tileNames = generateTilenames(tilesRc)
        
        tiles = [0 for i in xrange(len(tileNames))]
        tilesByName = dict()
        
        for i in xrange(len(tileNames)):
            tileName = tileNames[i]
            rawSpec = tilesRc.getProperty(tileName)
            if rawSpec is None:
                break
            
            ts = parseTileSpec(i, tileName, rawSpec, tilesRc)
            tilesByName[tileName] = ts
            tiles[i] = ts
            
        for i in xrange(len(tiles)):
            tiles[i].resolveReferences(tilesByName)
            bi = tiles[i].getBuildingInfo()
            if bi is not None:
                for j in xrange(len(bi.members)):
                    tId = bi.members[j]
                    offX = (-1 if (bi.width >= 3) else 0) + j % bi.width
                    offY = (-1 if bi.height >= 3 else 0) + j / bi.width
                    
                    if (tiles[tId].owner is None 
                            and (offX != 0 or offY != 0)):
                        tiles[tId].owner = tiles[i]
                        tiles[tId].ownerOffsetX = offX
                        tiles[tId].ownerOffsetY = offY
        self._tiles = tiles
        self._tilesByName = tilesByName


