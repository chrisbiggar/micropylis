'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
from pyglet.window import key
from pyglet.window.key import KeyStateHandler
from pyglet.graphics import OrderedGroup
from pyglet.gl import glPushMatrix, glPopMatrix, glTranslatef
from tileImages import TileImagesBySize, SizeNotAvaiableError
from pyglet.sprite import Sprite
from engine.misc import create2dArray

class Keys(KeyStateHandler):
    '''
        responds to keypresses, notifying an event handler
        while storing the current state of the keys for querying.
    '''
    def __init__(self, parent):
        self.parent = parent

    def on_key_press(self, symbol, modifiers):
        try:
            self.parent.key_press(symbol, modifiers)
        except AttributeError:
            # parent does not impl key_press method
            pass
        super(Keys, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        try:
            self.parent.key_release(symbol, modifiers)
        except AttributeError:
            # parent does not impl key_release method
            pass
        super(Keys, self).on_key_release(symbol, modifiers)
        

class TilesGroup(OrderedGroup):
    def __init__(self):
        super(TilesGroup, self).__init__(1)
        self.focusX = 0
        self.focusY = 0
        
    def setFocus(self, x=None, y=None):
        if x is not None:
            self.focusX = x
        if y is not None:
            self.focusY = y

    def set_state(self):
        glPushMatrix()
        glTranslatef(float(-self.focusX),float(self.focusY),0.)
        
    def unset_state(self):
        glPopMatrix()
        
        
        
'''
class ViewingPane

Displays the Map to the user and allows the current
tool to act on the map at spot where user clicks

NOTES
(none)
'''
class ViewingPane(object):
    DEFAULT_TILE_SIZE = 16

    def __init__(self, engine, width, height):
        self.setSize(width, height)
        try:
            self.tileImages = TileImagesBySize(self.DEFAULT_TILE_SIZE)
        except SizeNotAvaiableError:
            print "Invalid default size: " + str(self.DEFAULT_TILE_SIZE)
        self._group = TilesGroup()
        self.keys = Keys(self)
        self.reset(engine)
        
    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.tileImages.higherSize()
            self._resetTileBatch()
        if symbol == key.MINUS:
            self.tileImages.lowerSize()
            self._resetTileBatch()
        
    def reset(self, engine):
        self.scrollX = 0
        self.scrollY = 0
        self.setEngine(engine)
        self._resetTileBatch()
        
    def moveView(self, mx, my):
        if mx != 0:
            self._setScroll(x=mx+self.scrollX)
        if my != 0:
            self._setScroll(y=my+self.scrollY)
        
    def _setScroll(self, x=None, y=None):
        ''' keeps within limits of map '''
        if x is not None:
            maxX = (self._engine.getWidth() * 
                    self.tileImages.currentTileSize()) - self._width
            self.scrollX = max(0,x)
            self.scrollX = min(maxX,self.scrollX)
        if y is not None:
            maxY = (self._engine.getHeight() * 
                    self.tileImages.currentTileSize()) - self._height
            self.scrollY = max(0,y)
            self.scrollY = min(maxY,self.scrollY)
        self._group.setFocus(self.scrollX, self.scrollY)
    
    def setSize(self, width, height):
        self._width = width
        self._height = height
            
    def setEngine(self, eng):
        self._engine = eng
        self._engine.push_handlers(self)
        
    def _resetTileBatch(self):
        self.tileBatch = pyglet.graphics.Batch()
        tileSize = self.tileImages.currentTileSize()
        mapWidth = self._engine.getWidth()
        mapHeight = self._engine.getHeight()
        self._tileSprites = create2dArray(mapWidth, mapHeight)
        for y in range(mapHeight):
            for x in range(mapWidth):
                cell = self._engine.getTile(x,y)
                image = self.tileImages.getTileImage(cell)
                y2 = (self._height - (y*tileSize)) - tileSize
                self._tileSprites[x][y] = Sprite(image,
                                        x=x*tileSize, y=y2,
                                        batch=self.tileBatch,
                                        group=self._group)
        

    def on_map_changed(self, tilesList):
        '''
        modifies tile batch TODO this description
        '''
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            self._tileSprites[x][y].delete()
            tileSize = self.tileImages.currentTileSize()
            cell = self._engine.getTile(x,y)
            image = self.tileImages.getTileImage(cell)
            y2 = (self._height - (y*tileSize)) - tileSize
            self._tileSprites[x][y] = Sprite(image,
                                    x=x*tileSize, y=y2,
                                    batch=self.tileBatch,
                                    group=self._group)
            
    def _checkScrollKeys(self, dt):
        # move 12 tiles per second
        delta = int(12 * self.tileImages.currentTileSize() * dt) 
        if (self.keys[key.LEFT]):
            self.moveView(-delta, 0)
        elif (self.keys[key.RIGHT]):
            self.moveView(delta, 0)
        if (self.keys[key.DOWN]):
            self.moveView(0, delta)
        elif (self.keys[key.UP]):
            self.moveView(0, -delta)
        
    def update(self, dt):
        self._checkScrollKeys(dt)
        

            

        
        
        
        
        
        
        
        
        