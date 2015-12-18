'''
Created on Aug 30, 2015

@author: chris
'''
from pyglet.window import key
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite
from engine.cityLocation import CityLocation
from tileImages import TileImages
import gui
import engine
from util import create2dArray
from engine.tileConstants import CLEAR
from pyglet.gl import *
import math
from pyglet import clock
from engine import tileConstants
from engine.speed import Speed


class TileSprite(Sprite):
    '''
        static buffer object usage hint because only texture will change.
    '''
    def __init__(self, tileNum, x, y, batch, group, tileImages, clock):
        self.tileImages = tileImages
        super(TileSprite,self).__init__(
                            self.tileImages.getTileImage(tileNum),
                            x=x,
                            y=y,
                            batch=batch,
                            group=group,
                            usage='static',
                            custom_clock=clock)
    
    def setTile(self, tileNum):
        self.image = self.tileImages.getTileImage(tileNum)



class TilesGroup(OrderedGroup):
    def __init__(self, order=1):
        super(TilesGroup, self).__init__(order)
        self.focusX = 0
        self.focusY = 0
        self.zoom = 1.0
        self.yTrans = 0
        
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
        glTranslatef(0.,self.yTrans, 0.)
        glTranslatef(float(self.focusX),float(self.focusY),0.)
        glTranslatef(self.zoomPointX, self.zoomPointY,0.0)
        glScalef(self.zoom,self.zoom,1.0)
        glTranslatef(-self.zoomPointX,-self.zoomPointY,0.0)
        
        
    def unset_state(self):
        glPopMatrix()


class BlinkOverlayGroup(OrderedGroup):
    def __init__(self, tilesGroup):
        super(BlinkOverlayGroup,self).__init__(2)
        self._tilesGroup = tilesGroup
        self.blink = False
        self.lastChange = 0
        self.dt = 0
        self.freq = 0.8
        self.paused = False
        
    def set_state(self):
        self._tilesGroup.set_state()
        if self.blink and not self.paused:
            glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
    
    def unset_state(self):
        self._tilesGroup.unset_state()
        if self.blink and not self.paused:
            glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
    
    def start(self):
        self.paused = False
        
    def stop(self):
        self.paused = True
    
    def update(self, dt):
        self.dt += dt
        if self.dt > self.lastChange + self.freq:
            self.blink = not self.blink
            self.lastChange = self.dt

        
class ToolCursorGroup(OrderedGroup):
    def __init__(self, tilesGroup):
        super(ToolCursorGroup,self).__init__(3)
        self._tilesGroup = tilesGroup
    
    def set_state(self):
        self._tilesGroup.set_state()
    
    def unset_state(self):
        self._tilesGroup.unset_state()
    


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
    #DH = 660
    DEFAULT_TILE_SIZE = 16
    INCREASE = 2
    DECREASE = 1

    def __init__(self, engine, x, y, width, height):
        self.animCoefficient = 0
        self.animClock = clock.Clock(time_function=self.getTime)
        self.keys = gui.Keys(self)
        
        # zoom related vars
        self.zoomSpeed = float(gui.config.get('misc', 'ZOOM_TRANSITION_SPEED'))
        self.zoomChange = float(gui.config.get('misc', 'ZOOM_INCREMENT'))
        self.scrollSpeed = int(gui.config.get('misc', 'KEY_SCROLL_SPEED'))
        self._scaleOffX = 0
        self._scaleOffY = 0
        self._zoom = 1.0
        self._targetZoom = self._zoom
        self.zoomTransition = None
        
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        
        self.tileImages = TileImages(self.DEFAULT_TILE_SIZE)
        self._tilesGroup = TilesGroup()
        self._cursorGroup = ToolCursorGroup(self._tilesGroup)
        self._tilesGroup.setViewportSize(width, height)
        self.overlayGroup = OrderedGroup(2)
        self._tileSprites = None
        self.blinkGroup = BlinkOverlayGroup(self._tilesGroup)
        
        self.reset(engine)
    
    
    def on_power_indicator_changed(self, pos):
        x = pos[0]
        y = pos[1]
        ind = self._engine.getTileIndicator(x,y)
        if ind and self._tileIndicators[x][y] is None:
            img = self.tileImages.getTileImage(tileConstants.LIGHTNINGBOLT)
            tileSize = self.DEFAULT_TILE_SIZE
            x2 = x * tileSize
            y2 = (self._height - y * tileSize - tileSize)
            self._tileIndicators[x][y] = Sprite(img,
                                                batch=self.batch,
                                                group=self.blinkGroup,
                                                x=x2,
                                                y=y2)
        if not ind and self._tileIndicators[x][y] is not None:
            self._tileIndicators[x][y].delete()
            self._tileIndicators[x][y] = None
    
        
    def reset(self, engine):
        self._scrollX = 0
        self._scrollY = 0
        self.toolCursor = None
        self.toolPreview = None
        self.setEngine(engine)
        self._resetTileBatch()
        self._tileIndicators = create2dArray(
                                    self._engine.getHeight(), 
                                    self._engine.getWidth(), 
                                    None)
        
        
    def resize(self, width, height):
        if self._width == width and self._height == height:
            return
        self._tilesGroup.setViewportSize(width, height)
        self._width = width
        self._height = height
        self.upOff()
        self._tilesGroup.yTrans = height - 660
            
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
            x,y,x2,y2 = self.expandMapCoords(self.toolCursor.rect)
            
            c = self.toolCursor.fillColor
            colorData = []
            numVertices = 4
            for i in range(numVertices * len(c)):
                i2 = i % numVertices
                colorData.append(c[i2])
            self.toolCursor.vl = self.batch.add(numVertices,
                                    GL_QUADS,
                                    self._cursorGroup,
                                    ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                    ('c4B', colorData))
        
    def newToolCursor(self, newRect, tool):
        newCursor = ToolCursor()
        newCursor.rect = newRect
        
        #tc.borderColor = (0, 200, 200)
        roadsBg = gui.config.get('tools.bgcolor', tool.name)
        newCursor.fillColor = map(int, tuple(roadsBg.split(',')))
        
        self.setToolCursor(newCursor)
        
    
    def expandMapCoords(self, rect):
        '''
            world-space coordinates of tile coord
        '''
        tileSize = self.DEFAULT_TILE_SIZE
        x = self.toolCursor.rect.x * tileSize
        y = (self._height - (self.toolCursor.rect.y - 1)
                       * tileSize - tileSize)
        x2 = x + self.toolCursor.rect.width * tileSize
        y2 = y + self.toolCursor.rect.height * tileSize
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
                    tNum = newPreview.getTile(x2,y2)
                    if tNum != CLEAR:
                        self._tileSprites[x2][y2].setTile(tNum)
        self.toolPreview = newPreview
        

    def evToCityLocation(self, x, y):
        '''
            returns city relative location from gui coords
        '''
        tileSize = self.DEFAULT_TILE_SIZE
        # transformed coords:
        x = math.floor((x - self._scaleOffX) / self._zoom + self._scrollX)
        
        y = math.floor((self._height - y - self._scaleOffY)
                        / self._zoom + self._scrollY)
        #print y,self._height,self._scaleOffY,self._scrollY
        return CityLocation(int(x / tileSize), int(y / tileSize))
    
    def getScroll(self):
        return (self._scrollX, self._scrollY)
    
    def getHeight(self):
        return self._height
    
    def getWidth(self):
        return self._width
    
    def printWorldCoords(self,x,y):
        ''' debugging fncn: print world coords from screen coords
        '''
        #print x,self._scaleOffX,self._scrollX,self._zoom
        x = math.floor((x - self._scaleOffX) / self._zoom + self._scrollX)
        #print y,self._scaleOffY,self._scrollY,self._zoom
        y = (math.floor(((self._height - y) - self._scaleOffY)
                        / self._zoom + self._scrollY))
        print "World Coords: " + str((x,y))
        
    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.setZoom(increment=self.zoomChange)
        if symbol == key.MINUS:
            self.setZoom(increment=-self.zoomChange)
        if symbol == key._0:
            self.setZoom(newValue=1.0)
            
    def getTime(self):
        ''' dilates time for controlling animation clock speed'''
        return clock._default_time_function() * self.animCoefficient
            
    def setSpeed(self, lastSpeed, speed):
        if lastSpeed:
            lastSpeed.lastTs = self.getTime()
        self.animClock.restore_time(speed.lastTs)
        self.animCoefficient = speed.animCoefficient
        if speed == engine.speed.PAUSED:
            self.blinkGroup.stop()
        else:
            self.blinkGroup.start()
            
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
            self.deltaZoom = (newValue - self._zoom) * 3
            if newValue > self._zoom:
                self.zoomTransition = self.INCREASE
            elif newValue < self._zoom:
                self.zoomTransition = self.DECREASE
                    
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
            width = ((self._engine.getWidth() *
                     (self.DEFAULT_TILE_SIZE * zoom))
                     - self._width) / zoom
            minX = math.ceil(self._scaleOffX / zoom)
            maxX = math.floor(minX + width)
            self._scrollX = max(minX,x)
            self._scrollX = min(maxX,self._scrollX)
        if y is not None:
            height = ((self._engine.getHeight() * self.DEFAULT_TILE_SIZE * zoom) 
                    - self._height) / zoom
            minY = math.floor(self._scaleOffY / zoom)
            maxY = math.floor(minY + height)
            self._scrollY = max(minY,y)
            self._scrollY = min(maxY,self._scrollY)
        self._tilesGroup.setFocus(-self._scrollX, self._scrollY)
        
    def _resetTileBatch(self):
        mapWidth = self._engine.getWidth()
        mapHeight = self._engine.getHeight()
        if self._tileSprites is not None:
            for y in range(mapHeight):
                for x in range(mapWidth):
                    if self._tileSprites[x][y] is not None:
                        self._tileSprites[x][y].delete()
        else:
            self._tileSprites = create2dArray(mapWidth, mapHeight, None)
        self.batch = pyglet.graphics.Batch()
        tileSize = self.DEFAULT_TILE_SIZE
        for y in range(mapHeight):
            for x in range(mapWidth):
                cell = self._engine.getTile(x,y)
                x2 = (x * tileSize)
                y2 = (self._height - y * tileSize - tileSize)
                self._tileSprites[x][y] = TileSprite(cell,
                                    x2,
                                    y2,
                                    self.batch,
                                    self._tilesGroup,
                                    self.tileImages,
                                    self.animClock)

    def on_map_changed(self, tilesList):
        '''
        modifies tile batch with tilesList
        '''
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            cell = self._engine.getTile(x,y)
            self._tileSprites[x][y].setTile(cell)
            
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
    
    def upOff(self):
        self._scaleOffX = math.floor((self._width/2) * (1-self._zoom))
        self._scaleOffY = math.floor((self._height/2) * (1-self._zoom))
        self.validateScroll(self._zoom)
    
    def updateZoom(self, dt):
        self._zoom += self.deltaZoom * dt
        if ((self.zoomTransition == self.INCREASE and
                self._zoom >= self._targetZoom) or
                (self.zoomTransition == self.DECREASE and\
                self._zoom <= self._targetZoom)):
            self.zoomTransition = None
            self._zoom = self._targetZoom
        self._tilesGroup.zoom = self._zoom
        self.upOff()
        self.setToolCursor(self.toolCursor)
        

    def update(self, dt):
        self._checkScrollKeys(dt)
        if self.zoomTransition is not None:
            self.updateZoom(dt)
        self.blinkGroup.update(dt)
        
        
        
        
        
        
        
        
        