'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
#from pyglet.sprite import Sprite
import array
from engine.tileConstants import *

class SizeNotAvaiableException(Exception):
    pass

'''
class TileImagesBySize

default tile size must be specified at creation
'''
class TileImagesBySize(object):
    def __init__(self, defaultSize):
        #self.smallTiles = TileImages(8)
        self.mediumTiles = TileImages(16)
        #self.largeTiles = TileImages(32)
        self.sizes = dict()
        #self.sizes['8'] = self.smallTiles
        self.sizes['16'] = self.mediumTiles
        #self.sizes['32'] = self.largeTiles
        self.defaultSize = defaultSize
        self.setCurrentSize(defaultSize)
        
    def setSizeDefault(self):
        self.setCurrentSize(self.defaultSize)
        
    def setCurrentSize(self, size):
        try:
            self.curTileImages = self.sizes[str(size)]
            self.currentSize = size
        except KeyError:
            raise SizeNotAvaiableException()
        
    def getTileImage(self, cell):
        return self.curTileImages.getTileImage(cell)
    
    def getTileSize(self):
        return self.currentSize

'''
class TileImages
Makes available the individual images for each tile in a set.
Images are loaded from a given filename in sequential fashion, and are
referenced by their index into that sequence.
'''
class TileImages(object):
    '''
    
    '''
    def __init__(self, tileSize):
        self.tileSize = tileSize
        self.tileSheetFile = 'tiles.png'
        self.tiles = self.loadTileImages()
        
    def loadTileImages(self):
        tileSheet = pyglet.image.load(self.tileSheetFile)
        self.numTiles = tileSheet.height / self.tileSize
        tiles = pyglet.image.ImageGrid(tileSheet, self.numTiles, 1)
        return pyglet.image.TextureGrid(tiles)
    
    def getTileImage(self, cell):
        tile = (self.numTiles - (cell & LOMASK) - 1) % len(self.tiles)
        return self.tiles[tile]












