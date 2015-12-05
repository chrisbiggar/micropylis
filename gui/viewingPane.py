'''
Created on Aug 30, 2015

@author: chris
'''
from pyglet.window import key
from pyglet.window.key import KeyStateHandler
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite
from engine.cityLocation import CityLocation
from tileImages import TileImages
import gui
from util import create2dArray
from engine.tileConstants import CLEAR
from pyglet.gl import *
import math


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
        self.zoom = 1.0
        
    def setViewportSize(self, width, height):
        self.viewWidth = width
        self.viewHeight = height
        self.reCalc()
        
    def setFocus(self, x=None, y=None):
        if x is not None:
            self.focusX = x
        if y is not None:
            self.focusY = y
        self.reCalc()
            
    def reCalc(self):
        self.zoomPointX = -self.focusX + (self.viewWidth / 2)
        self.zoomPointY = -self.focusY + (self.viewHeight / 2)

    def set_state(self):
        '''
            translates tilemap to zoom into centre of viewport.
        '''
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(float(self.focusX),float(self.focusY),0.)
        glTranslatef(self.zoomPointX, self.zoomPointY,0.0)
        glScalef(self.zoom,self.zoom,1.0)
        glTranslatef(-self.zoomPointX,-self.zoomPointY,0.0)
        
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
'''
class ViewingPane(object):
    DEFAULT_TILE_SIZE = 16

    def __init__(self, engine, x, y, width, height):
        self.zoomSpeed = float(gui.config.get('misc', 'ZOOM_TRANSITION_SPEED'))
        self.zoomChange = float(gui.config.get('misc', 'ZOOM_INCREMENT'))
        self.scrollSpeed = int(gui.config.get('misc', 'KEY_SCROLL_SPEED'))
        self.xOff = 0
        self.yOff = 0
        self._zoom = 1.0
        self._targetZoom = self._zoom
        self.inZoomTransition = False
        
        self.x = x
        self.y = y
        self.setSize(width, height)
        self.tileImages = TileImages(self.DEFAULT_TILE_SIZE)
        self._tilesGroup = TilesGroup()
        self._tilesGroup.setViewportSize(width, height)
        self.overlayGroup = OrderedGroup(2)
        self.keys = Keys(self)
        self.reset(engine)
        
    def reset(self, engine):
        self._scrollX = 0
        self._scrollY = 0
        self.toolCursor = None
        self.toolPreview = None
        self.setEngine(engine)
        self._resetTileBatch()
        #self._setScroll(-self.xOff, self._scrollY)
        
    def setSize(self, width, height):
        self._width = width
        self._height = height
            
    def setEngine(self, eng):
        self._engine = eng
        self._engine.push_handlers(self)
        
    def withinRange(self, x, y):
        # screen space coordinates
        return x >= self.x and x <= self.x + self._width\
            and y >= self.y and y <= self.y + self._height
            
    def setToolCursor(self, newCursor):
        if self.toolCursor is None\
            and self.toolCursor == newCursor:
            return
        
        if self.toolCursor is not None and\
                self.toolCursor.vl is not None:
            self.toolCursor.vl.delete()
            
        self.toolCursor = newCursor
        
        if self.toolCursor is not None:
            x,y,x2,y2 = self.cityRectToScreenCoords(self.toolCursor.rect)
            
            c = self.toolCursor.fillColor
            colorData = []
            numVertices = 4
            for i in range(numVertices * len(c)):
                i2 = i % numVertices
                colorData.append(c[i2])
            self.toolCursor.vl = self.tileBatch.add(numVertices,
                                    GL_QUADS,
                                    self.overlayGroup,
                                    ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                    ('c4B', colorData))
        
    def newToolCursor(self, newRect, tool):
        newCursor = ToolCursor()
        newCursor.rect = newRect
        
        #tc.borderColor = (0, 200, 200)
        roadsBg = gui.config.get('tools.bgcolor', tool.name)
        newCursor.fillColor = map(int, tuple(roadsBg.split(',')))
        
        self.setToolCursor(newCursor)
        
    
    def cityRectToScreenCoords(self, rect):
        '''
        
        '''
        
        tileSize = self.DEFAULT_TILE_SIZE
        x = math.floor((rect.x * tileSize + 
                        (self.xOff / self._zoom - self._scrollX)) 
                       * self._zoom)
        y = math.floor((self._height - rect.y * tileSize + 
                        (self.yOff / self._zoom + self._scrollY)) 
                       * self._zoom)
        x2 = x + rect.width * tileSize * self._zoom
        y2 = y + rect.height * tileSize * self._zoom
        y2 = y - (y2 - y)
        return (x,y,x2,y2)
    
    
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
        tileSize = self.DEFAULT_TILE_SIZE
        # transformed coords:
        x = math.floor((x - self.xOff) / self._zoom + self._scrollX)
        y = math.floor((self._height - y - self.yOff)
                        / self._zoom + self._scrollY)
        return CityLocation(int(x / tileSize), int(y / tileSize))
    
    def getTileSize(self):
        return self.tileImages.currentTileSize()
    
    def getScroll(self):
        return (self._scrollX, self._scrollY)
    
    def getHeight(self):
        return self._height
    
    def getWidth(self):
        return self._width
    
    def printWorldCoords(self,x,y):
        ''' debugging fncn: print world coords from screen coords
        '''
        #print x,self.xOff,self._scrollX,self._zoom
        x = math.floor((x - self.xOff) / self._zoom + self._scrollX)
        #print y,self.yOff,self._scrollY,self._zoom
        y = (math.floor(((self._height - y) - self.yOff)
                        / self._zoom + self._scrollY))
        print "World Coords: " + str((x,y))
        
    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.setZoom(increment=self.zoomChange)
        if symbol == key.MINUS:
            self.setZoom(increment=-self.zoomChange)
        if symbol == key._0:
            self.setZoom(newValue=1.0)
            
    def setZoom(self, newValue=None, increment=None):
        '''
            pass one value but not both. changeZoom increments
        '''
        assert newValue or increment and not (newValue and increment)
        
        if increment:
            newValue = round(self._zoom * (1 + increment), 2)
            
        tileSize = self.DEFAULT_TILE_SIZE
        
        if (self._engine.getWidth() * tileSize * newValue
                >= self._width) and\
                (self._engine.getHeight() * tileSize * newValue
                 >= self._height):
            self._targetZoom = newValue
            self.inZoomTransition = True
                    
    def moveView(self, mx, my):
        if mx != 0:
            mx = mx / self._zoom
            self._setScroll(x=-mx+self._scrollX)
        if my != 0:
            my = my / self._zoom
            self._setScroll(y=my+self._scrollY)
            
    def validateScroll(self, zoom=None):
        self._setScroll(self._scrollX, self._scrollY, zoom)
        
    def _setScrollFree(self, x=None, y=None):
        ''' non restricted scrolling '''
        
        if x is not None:
            self._scrollX = x
        if y is not None:
            self._scrollY = y
        self._tilesGroup.setFocus(self._scrollX, self._scrollY)
        
    def _setScroll(self, x=None, y=None, zoom=None):
        ''' restricts within limits of map '''
        
        if zoom is None:
            zoom = self._zoom
        if x is not None:
            maxX = ((self._engine.getWidth() *
                     (self.DEFAULT_TILE_SIZE * zoom))
                     - self._width) / zoom
            minX = math.ceil(self.xOff / zoom)
            maxX = math.floor(minX + maxX)
            self._scrollX = max(minX,x)
            self._scrollX = min(maxX,self._scrollX)
        if y is not None:
            maxY = ((self._engine.getHeight() * self.DEFAULT_TILE_SIZE * zoom) 
                    - self._height) / zoom
            minY = math.floor(self.yOff / zoom)
            maxY = math.floor(minY + maxY)
            self._scrollY = max(minY,y)
            self._scrollY = min(maxY,self._scrollY)
        self._tilesGroup.setFocus(-self._scrollX, self._scrollY)
        
    def setTileSprite(self, tileNum, x, y):
        if self._tileSprites[x][y] is not None and\
                self._tileSprites[x][y].image is not None:
            self._tileSprites[x][y].delete()
        tileSize = self.DEFAULT_TILE_SIZE
        image = self.tileImages.getTileImage(tileNum)
        
        x2 = (x * tileSize)
        y2 = (self._height - y * tileSize - tileSize)
        self._tileSprites[x][y] = Sprite(image,
                            x=x2,
                            y=y2,
                            batch=self.tileBatch,
                            group=self._tilesGroup)
        
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
        modifies tile batch with tilesList
        '''
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            cell = self._engine.getTile(x,y)
            self.setTileSprite(cell, x, y)
            
    def _checkScrollKeys(self, dt):
        # move 12 tiles per second
        delta = int(self.scrollSpeed * self.DEFAULT_TILE_SIZE * dt) 
        if (self.keys[key.LEFT]):
            self.moveView(delta, 0)
        elif (self.keys[key.RIGHT]):
            self.moveView(-delta, 0)
        if (self.keys[key.DOWN]):
            self.moveView(0, delta)
        elif (self.keys[key.UP]):
            self.moveView(0, -delta)
    
    def updateZoom(self, dt):
        if self._zoom > self._targetZoom:
            self._zoom -= self.zoomSpeed * dt
            if self._zoom <= self._targetZoom:
                self.inZoomTransition = False
                self._zoom = self._targetZoom
        elif self._zoom < self._targetZoom:
            self._zoom += self.zoomSpeed * dt
            if self._zoom >= self._targetZoom:
                self.inZoomTransition = False
                self._zoom = self._targetZoom
        self._tilesGroup.zoom = self._zoom
        self.xOff = math.floor((self._width/2) * (1-self._zoom))
        self.yOff = math.floor((self._height/2) * (1-self._zoom))
        self.validateScroll(self._zoom)

    def update(self, dt):
        self._checkScrollKeys(dt)
        if self.inZoomTransition:
            self.updateZoom(dt)
        
        
        
        
        
        
        
        
        