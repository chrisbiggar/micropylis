'''
Created on Aug 30, 2015

@author: chris
'''
import math
import pyglet
from pyglet.window import key
from pyglet.window.key import KeyStateHandler
from pyglet.graphics import OrderedGroup
from pyglet.gl import glPushMatrix, glPopMatrix, glTranslatef, GL_QUADS, glScalef
from pyglet.sprite import Sprite
from engine.cityLocation import CityLocation
from engine.cityRect import CityRect
from tileImages import TileImagesBySize, SizeNotAvaiableError
import gui
from util import create2dArray
from engine.tileConstants import CLEAR


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
        
class OverlayGroup(OrderedGroup):
    def __init__(self):
        super(OverlayGroup,self).__init__(2)
        
class ToolCursor(object):
    def __init__(self):
        self.rect = None # CityRect
        #self.borderColor = None
        self.fillColor = None
        self.vl = None
        
'''
class ViewingPane

Displays the Map to the user and allows the current
tool to act on the map at spot where user clicks

NOTES
(none)
'''
class ViewingPane(object):
    DEFAULT_TILE_SIZE = 16

    def __init__(self, engine, x, y, width, height):
        self.x = x
        self.y = y
        self.setSize(width, height)
        try:
            self.tileImages = TileImagesBySize(self.DEFAULT_TILE_SIZE)
        except SizeNotAvaiableError:
            print "Invalid default size: " + str(self.DEFAULT_TILE_SIZE)
        self._group = TilesGroup()
        self.keys = Keys(self)
        self.reset(engine)
        
    def reset(self, engine):
        self._scrollX = 0
        self._scrollY = 0
        self.toolCursor = None
        self.toolPreview = None
        self.setEngine(engine)
        self._resetTileBatch()
        
    def setSize(self, width, height):
        self._width = width
        self._height = height
            
    def setEngine(self, eng):
        self._engine = eng
        self._engine.push_handlers(self)
        
    def withinRange(self, x, y):
        #print self.x, self._width
        return x >= self.x and x <= self.x + self._width\
            and y >= self.y and y <= self.y + self._height
        
    def setToolCursor(self, newRect, tool):
        tc = ToolCursor()
        tc.rect = newRect
        
        #tc.borderColor = (0, 200, 200)
        roadsBg = gui.config.get('tools.bgcolor', tool.name)
        tc.fillColor = map(int, tuple(roadsBg.split(',')))
        
        self.setToolCursor2(tc)
        
    def cityRectToScreenCoords(self, rect):
        '''
            used currently only for toolcursor.
            if being used for pyglet sprite, y needs to be adjusted
            by subtracing the tilesize.
        '''
        tileSize = self.tileImages.currentTileSize()
        x = rect.x * tileSize - self._scrollX
        y = self._height - rect.y * tileSize + self._scrollY
        x2 = x + rect.width * tileSize
        y2 = y + rect.height * tileSize
        y2 = y - (y2 - y)
        return (x,y,x2,y2)
        
    def setToolCursor2(self, newCursor):
        if self.toolCursor is None\
            and self.toolCursor == newCursor:
            return
        
        self.toolCursor = newCursor
        
        if self.toolCursor is not None:
            x,y,x2,y2 = self.cityRectToScreenCoords(self.toolCursor.rect)
            
            c = self.toolCursor.fillColor
            self.toolCursor.vl = pyglet.graphics.vertex_list(4, 
                            ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                            ('c4B', [c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]]))

    def setToolPreview(self, newPreview):
        '''
            
        '''
        
        if self.toolPreview is not None:
            # reset old preview tile sprites
            b = self.toolPreview.getBounds()
            tilesList = list()
            for x in range(b.width):
                for y in range(b.height):
                    tilesList.append(
                                (x + b.x,
                                 y + b.y))
            self.on_map_changed(tilesList)
        
        if newPreview is not None:
            # set new preview tile sprites
            b = newPreview.getBounds()
            for y in range(b.height):
                for x in range(b.width):               
                    x2 = x - newPreview.offsetX
                    y2 = y - newPreview.offsetY
                    t = newPreview.getTile(x2,y2)
                    if t != CLEAR:
                        self.setTileSprite(t, x2, y2)
        self.toolPreview = newPreview
        

    def evToCityLocation(self, x, y):
        '''
            returns city relative location from gui coords
        '''
        tileSize = self.tileImages.currentTileSize()
        x = self._scrollX + x
        y = self._scrollY + (self._height - y)
        return CityLocation(int(x / tileSize), int(y / tileSize))
    
    def getTileSize(self):
        return self.tileImages.currentTileSize()
    
    def getScroll(self):
        return (self._scrollX, self._scrollY)
    
    def getHeight(self):
        return self._height
    
    def getWidth(self):
        return self._width
        
    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.tileImages.higherSize()
            self._resetTileBatch()
        if symbol == key.MINUS:
            self.tileImages.lowerSize()
            self._resetTileBatch()
        
    def moveView(self, mx, my):
        if mx != 0:
            self._setScroll(x=mx+self._scrollX)
        if my != 0:
            self._setScroll(y=my+self._scrollY)
        
    def _setScroll(self, x=None, y=None):
        ''' keeps within limits of map '''
        if x is not None:
            maxX = (self._engine.getWidth() * 
                    self.tileImages.currentTileSize()) - self._width
            self._scrollX = max(0,x)
            self._scrollX = min(maxX,self._scrollX)
        if y is not None:
            maxY = (self._engine.getHeight() * 
                    self.tileImages.currentTileSize()) - self._height
            self._scrollY = max(0,y)
            self._scrollY = min(maxY,self._scrollY)
        self._group.setFocus(self._scrollX, self._scrollY)
        
    def setTileSprite(self, tileNum, x, y):
        if self._tileSprites[x][y] is not None and\
                self._tileSprites[x][y].image is not None:
            self._tileSprites[x][y].delete()
        tileSize = self.tileImages.currentTileSize()
        image = self.tileImages.getTileImage(tileNum)
        x2 = x * tileSize
        y2 = self._height - y * tileSize - tileSize
        self._tileSprites[x][y] = Sprite(image,
                            x=x2,
                            y=y2,
                            batch=self.tileBatch,
                            group=self._group)
        
    def _resetTileBatch(self):
        mapWidth = self._engine.getWidth()
        mapHeight = self._engine.getHeight()
        self._tileSprites = create2dArray(mapWidth, mapHeight, None)
        self.tileBatch = pyglet.graphics.Batch()
        for y in range(mapHeight):
            for x in range(mapWidth):
                cell = self._engine.getTile(x,y)
                self.setTileSprite(cell, x, y)
        

    def on_map_changed(self, tilesList):
        '''
        modifies tile batch TODO this description
        '''
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            cell = self._engine.getTile(x,y)
            self.setTileSprite(cell, x, y)
            
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
        

            

        
        
        
        
        
        
        
        
        