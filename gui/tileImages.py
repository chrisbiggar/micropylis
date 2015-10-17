'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
from engine.tileConstants import *
import new
from distutils.ccompiler import new_compiler

class SizeNotAvaiableError(Exception):
    pass


class Limits(object):
    '''
    
    '''
    def __init__(self):
        self.min = None
        self.max = None
        
    def setMin(self, m):
        self.min = m
        
    def setMax(self, m):
        self.max = m
        
    def update(self, new):
        if self.min == None:
            self.min = new
            self.max = new
            return
        if new < self.min:
            self.min = new
        elif new > self.max:
            self.max = new
        
    def withinRange(self, x):
        if x >= self.min and x <= self.max:
            return True
        else:
            return False

'''
class TileImagesBySize

default tile size must be specified at creation
'''
class TileImagesBySize(object):
    def __init__(self, defaultSize):
        self._curTileImages = None
        self._limits = Limits()
        self._sizes = dict()
        self._addSize(TileImages(8))
        self._addSize(TileImages(16))
        self._addSize(TileImages(32))
        self._defaultSize = defaultSize
        self.setCurrentSize(defaultSize)
        
        
    def getTileImage(self, cell):
        return self._curTileImages.getTileImage(cell)
    
    def currentTileSize(self):
        return self._curTileImages.tileSize
        
    def _addSize(self, size):
        self._limits.update(size.tileSize)
        self._sizes[str(size.tileSize)] = size
        
    def setCurrentSize(self, size):
        try:
            self._curTileImages = self._sizes[str(size)]
            self._currentSize = size
        except KeyError:
            raise SizeNotAvaiableError()
        
    def defaultSize(self):
        self.setCurrentSize(self._defaultSize)
    
    def higherSize(self):
        new = self._currentSize * 2
        if self._limits.withinRange(new):
            self.setCurrentSize(new)
        
    def lowerSize(self):
        new = self._currentSize / 2
        if self._limits.withinRange(new):
            self.setCurrentSize(new)

'''
class TileImages
Makes available the individual images for each tile in a set.
Images are loaded from a given filename in sequential fashion, and are
referenced by their index into that sequence.
'''
class TileImages(object):
    def __init__(self, tileSize):
        self.tileSize = tileSize
        self._tileSheetFilename = 'res/tiles' + str(tileSize) + '.png'
        self._tiles = self.loadTileImages()
        
    def loadTileImages(self):
        tileSheet = pyglet.image.load(self._tileSheetFilename)
        rows = tileSheet.height / self.tileSize
        columns = tileSheet.width / self.tileSize
        return pyglet.image.TextureGrid(
                            pyglet.image.ImageGrid(tileSheet, rows, columns))
    
    def getTileImage(self, cell):
        # low 10 bits give tile index number
        return self._tiles[(cell & LOMASK) % len(self._tiles)]












