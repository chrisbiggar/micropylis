'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
from pyglet.window import key
from pyglet.window.key import KeyStateHandler
from tileImages import TileImages, TileImagesBySize, SizeNotAvaiableException
from pyglet.sprite import Sprite
from xml.etree.ElementInclude import include

class Keys(KeyStateHandler):
    '''
        responds to keypresses, notifying an event handler
        while storing the current state of the keys for querying
    '''
    def __init__(self, parent):
        self.parent = parent

    def on_key_press(self, symbol, modifiers):
        self.parent.key_press(symbol, modifiers)
        super(Keys, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.parent.key_release(symbol, modifiers)
        super(Keys, self).on_key_release(symbol, modifiers)

'''
class ViewingPane

Displays the Map to the user and allows the current
tool to act on the map at spot where user clicks

NOTES
- scrolling is done by directional keys for now (scrollX and scrollY)
'''
class ViewingPane(object):
    DEFAULT_TILE_SIZE = 16

    def __init__(self, engine, width, height):
        self.tileBatch = pyglet.graphics.Batch()
        self.reset(engine)
        self.setSize(width, height)
        self.selectTileSize()
        self.keys = Keys(self)
        
    def reset(self, engine):
        self.scrollX = 0
        self.scrollY = 0
        self.setEngine(engine)
        self.doTileUpdate = True
        
    def key_press(self, symbol, modifiers):
        pass
    def key_release(self, symbol, modifiers):
        inc = 32
        tileSize = 16 #self.tileImages.getTileSize()
        maxX = (self.engine.getWidth() * tileSize) - self.width
        maxY = ((self.engine.getHeight() - 1) * tileSize) - self.height
        if (symbol == key.LEFT):
            self.doTileUpdate = True
            self.scrollX = max(0, self.scrollX - inc)
        elif (symbol == key.RIGHT):
            self.doTileUpdate = True
            self.scrollX = min(maxX, self.scrollX + inc)
        elif (symbol == key.DOWN):
            self.doTileUpdate = True
            self.scrollY = min(maxY-16, self.scrollY + inc)
        elif (symbol == key.UP):
            self.doTileUpdate = True
            self.scrollY = max(0, self.scrollY - inc)
    
    def setSize(self, width, height):
        self.width = width
        self.height = height
        
    def selectTileSize(self, newSize=None):
        if (newSize == None):
            newSize = self.DEFAULT_TILE_SIZE
        try:
            self.tileImages = TileImages(newSize)
        except SizeNotAvaiableException:
            print "Size: " + str(newSize) + " not available"
            
    def setEngine(self, eng):
        self.engine = eng
        
    def update(self, dt):
        if (self.doTileUpdate == True):
            self.doTileUpdate = False
            self.tileBatch = pyglet.graphics.Batch()
            self.sprites = list()
            mapWidth = self.engine.getWidth()
            mapHeight = self.engine.getHeight()
            tileSize = 16 #self.tileImages.getTileSize()
            
            scrollX = self.scrollX
            scrollY = self.scrollY
            # gen current viewport tile offsets
            minX = scrollX / tileSize
            minY = scrollY / tileSize
            maxX = minX + (self.width / tileSize)
            maxY = minY + (self.height / tileSize)
            
            iY = 0
            for y in range(minY, maxY):
                iX = 0
                for x in range(minX, maxX):
                    cell = self.engine.getTile(x,y)
                    image = self.tileImages.getTileImage(cell)
                    x2 = iX * tileSize
                    y2 = (self.height - (iY*tileSize)) - tileSize
                    self.sprites.append(Sprite(
                                image, x=x2, y=y2,
                                batch=self.tileBatch))
                    iX = iX + 1
                iY = iY + 1
            

        
        
        
        
        
        
        
        
        