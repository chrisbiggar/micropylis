'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
from pyglet.gl import (glMatrixMode,GL_PROJECTION,GL_MODELVIEW,
                        glPushMatrix,glPopMatrix,glLoadIdentity,
                        glOrtho,glColorMask,GL_FALSE,GL_TRUE)
from pyglet.window import key
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite

import gui
from gui.tileImageLoader import TileImageLoader
import microWindow
import layout

import engine
from engine.cityLocation import CityLocation
from engine.tileConstants import CLEAR
from engine import tileConstants
from util import create2dArray,createRect,createHollowRect


TILESIZE = 16
BG_GROUP_ORDER = 1
MG_GROUP_ORDER = 2
FG_GROUP_ORDER = 3



class ViewportGroup(OrderedGroup):
    '''
    ViewportGroup
    
    Pyglet rendering group. Allows a zoomable and panable orthographic viewport to
    be controlled. Does not allows one to view outside defined map size.
    Gradually zooms in and out. Inverts opengl's screen bottom up coordinate sys 
    so coords start at top and progress down.
    '''
    INCREASE_ZOOM = 2
    DECREASE_ZOOM = 1
    
    def __init__(self, order=BG_GROUP_ORDER):
        super(ViewportGroup, self).__init__(order)
        
        self.zoomSpeed = float(gui.config.get('misc', 'ZOOM_TRANSITION_SPEED'))
        self.zoomInFactor = float(gui.config.get('misc', 'ZOOM_INCREMENT'))
        self.zoomOutFactor = 1 / self.zoomInFactor
        self.zoomLevel = 1
        self.targetZoom = self.zoomLevel
        self.zoomTransition = None
        self.deltaZoom = 0
        self.zoomX = None
        self.zoomY = None
        
        self.mapWidth = 0
        self.mapHeight = 0
        self.zoomedWidth  = 0
        self.zoomedHeight = 0
        self.renderWidth = 0
        self.renderHeight = 0
        self.widgetWidth = 0
        self.widgetHeight = 0
        
        self.left   = 0
        self.right  = 0
        self.bottom = 0
        self.top    = 0
        
    def setMapSize(self, width, height):
        self.mapWidth = width
        self.mapHeight = height
        
    def setViewportSize(self, (width, height),
                                (windowWidth, windowHeight)):
        '''
        Allows the render and widget sizes to be defined,
        recalculating the viewport accordingly.
        '''
        self.renderWidth = windowWidth
        self.renderHeight = windowHeight
        self.widgetWidth = width
        self.widgetHeight = height

        x = self.zoomX or (self.widgetWidth / 2)
        y = self.zoomY or (self.widgetHeight / 2)
        self._setZoom(x, y, None)
        
    def changeFocus(self, dx, dy):
        #self.setFocus()
        pass
        
    def setFocus(self, dx, dy):
        '''
        setFocus
        
        Pans the view by the amount given in arguments,
        restricting the view within limits of map
        '''
        left = self.left - dx * self.zoomLevel
        bottom = self.bottom + dy * self.zoomLevel
        
        ''' restrict view '''
        maxLeft = self.mapWidth - self.zoomedWidth
        maxBottom = self.mapHeight - self.zoomedHeight
        
        left = max(0, left)
        left = min(maxLeft + 
                   (self.renderWidth - self.widgetWidth) 
                    * self.zoomLevel, left)
        right = left + self.zoomedWidth
        
        bottom = max(0, bottom)
        bottom = min(maxBottom, bottom)
        top = bottom + self.zoomedHeight
        
        self.left   = left
        self.right  = right
        self.bottom = bottom
        self.top    = top
        
    def _setZoom(self, x, y, newZoomLevel):
        '''
        sets an absolute zoom level, 
            focused on x and y given in world-space coords.
        will not allow zoom < 0.2 or so far out that
        outside of map borders would be revealed.
        '''
        if newZoomLevel is None:
            newZoomLevel = self.zoomLevel
        
        if .2 > newZoomLevel:
            ''' restricts zoom-in to a normal level '''
            return

        mouseX = x / float(self.renderWidth)
        mouseY = y / float(self.renderHeight)

        mouseXInWorld = self.left + mouseX * self.zoomedWidth
        mouseYInWorld = self.bottom + mouseY * self.zoomedHeight

        zoomedWidth  = self.renderWidth * newZoomLevel
        zoomedHeight = self.renderHeight * newZoomLevel

        left   = mouseXInWorld - mouseX * zoomedWidth
        right  = mouseXInWorld + (1 - mouseX) * zoomedWidth
        bottom = mouseYInWorld - mouseY * zoomedHeight
        top    = mouseYInWorld + (1 - mouseY) * zoomedHeight
        
        # restricts zoom so it will not reveal the outside of the map
        maxRight = (self.mapWidth + 
                    (self.renderWidth - self.widgetWidth)  
                        * self.zoomLevel)
        maxTop = self.mapHeight
        if left < 0:
            left = 0
            if zoomedWidth <= maxRight:
                right = zoomedWidth
            else:
                return
        if right > maxRight:
            right = maxRight
            if right - zoomedWidth >= 0:
                left = right - zoomedWidth
            else:
                return
        if bottom < 0:
            bottom = 0
            if zoomedHeight <= maxTop:
                top = zoomedHeight
            else:
                return
        if top > maxTop:
            top = maxTop
            if top - zoomedHeight >= 0:
                bottom = top - zoomedHeight
            else:
                return
        
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.zoomLevel = newZoomLevel
        self.zoomedWidth = zoomedWidth
        self.zoomedHeight = zoomedHeight
    
    def setZoom(self, x, y, newZoomLevel):
        '''
        triggers a change in zoom level
        '''
        self.targetZoom = newZoomLevel
        self.zoomX = x
        self.zoomY = y
        self.deltaZoom = (newZoomLevel - self.zoomLevel) * 10
        if newZoomLevel > self.zoomLevel:
            self.zoomTransition = self.INCREASE_ZOOM
        elif newZoomLevel < self.zoomLevel:
            self.zoomTransition = self.DECREASE_ZOOM

    def changeZoom(self, x, y, dy):
        '''
        allows zoom level to be changed incrementally
        by a predefined change factor.
        a negative dy will zoom out while a positive dy will zoom in.
        '''
        y = self.renderHeight - y
        
        # Get scale factor
        f = self.zoomInFactor if dy > 0 else self.zoomOutFactor if dy < 0 else 1
        
        newZoomLevel = self.zoomLevel * f
        self.setZoom(x, y, newZoomLevel)
        
    def updateZoomTransition(self, dt):
        if self.zoomTransition is not None:
            self._setZoom(self.zoomX, self.zoomY, 
                         self.zoomLevel + self.deltaZoom * dt)
            if ((self.zoomTransition == self.INCREASE_ZOOM and
                    self.zoomLevel >= self.targetZoom) or
                    (self.zoomTransition == self.DECREASE_ZOOM and\
                    self.zoomLevel <= self.targetZoom)):
                self.zoomTransition = None
                self._setZoom(self.zoomX, self.zoomY, self.targetZoom)
    
    def update(self, dt):
        self.updateZoomTransition(dt)

    def screenCoordsToCityLocation(self, x, y):
        '''
            returns city relative location from gui coords
        '''
        y = self.renderHeight - y
        mouse_x = x / float(self.renderWidth)
        mouse_y = y / float(self.renderHeight)
        
        mouse_x_in_world = self.left   + mouse_x * self.zoomedWidth
        mouse_y_in_world = self.bottom + mouse_y * self.zoomedHeight
        
        return CityLocation(int(mouse_x_in_world / TILESIZE), 
                            int(mouse_y_in_world / TILESIZE))
    
    def set_state(self):
        '''
            sets the viewport
        '''
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(self.left, self.right, self.top, self.bottom, 1, -1)

        
    def unset_state(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


class BlinkingGroup(OrderedGroup):
    '''
    BlinkingGroup
    
    Uses given class's state and adds a blink
    functionality.
    '''
    def __init__(self, tilesGroup):
        super(BlinkingGroup,self).__init__(MG_GROUP_ORDER)
        self.tilesGroup = tilesGroup
        self.blink = False
        self.lastChange = 0
        self.dt = 0
        self.freq = 0.8
        self.paused = False
        
    def set_state(self):
        self.tilesGroup.set_state()
        if self.blink:
            glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
    
    def unset_state(self):
        self.tilesGroup.unset_state()
        if self.blink:
            glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
    
    def start(self):
        self.paused = False
        
    def stop(self):
        self.paused = True
    
    def update(self, dt):
        self.dt += dt
        if self.dt > self.lastChange + self.freq and not self.paused:
            self.blink = not self.blink
            self.lastChange = self.dt


class ToolCursorGroup(OrderedGroup):
    def __init__(self, tilesGroup):
        super(ToolCursorGroup,self).__init__(FG_GROUP_ORDER)
        self._tilesGroup = tilesGroup
    
    def set_state(self):
        self._tilesGroup.set_state()
    
    def unset_state(self):
        self._tilesGroup.unset_state()


class ToolCursor(object):
    '''
    data structure for tool cursor visual
    '''
    def __init__(self):
        self.rect = None # CityRect
        self.fillColor = None
        self.borderColor = (0, 0, 0, 255)
        self.vl = None
        self.borderVL = None
        

class TileSprite(Sprite):
    '''
        static buffer object usage hint because only texture will change.
    '''
    def __init__(self, tileNum, x, y, batch, group, tileImages, clock):
        self.tileImages = tileImages
        super(TileSprite,self).__init__(
                            self.tileImages.getTileImage(tileNum),
                            x=x, y=y,
                            batch=batch,
                            group=group,
                            usage='static',
                            custom_clock=clock)
    
    def setTile(self, tileNum):
        self.image = self.tileImages.getTileImage(tileNum)
        
   
        
        
'''
class CityView

Controls the rendering of the city.


'''
class CityView(layout.Spacer):
    def __init__(self, animClock):
        super(CityView,self).__init__()
        
        self.engine = None
        
        self.animClock = animClock
        self.keys = microWindow.Keys(self)
        self.scrollSpeed = int(gui.config.get('misc', 'KEYBOARD_SCROLL_SPEED'))
        
        self.tileImages = TileImageLoader(
                            gui.config.get('misc', 'TILES_FILE'), 
                            TILESIZE, flipTilesVert=True, padding=2)
        
        self.tilesGroup = ViewportGroup()
        self.toolCursorGroup = ToolCursorGroup(self.tilesGroup)
        self.blinkingGroup = BlinkingGroup(self.tilesGroup)
        self.tileSprites = None
        
        self._scrollX = 0
        self._scrollY = 0
        self.toolCursor = None
        self.toolPreview = None
        self._tileIndicators = None
        self.engine = None
        
    def setEngine(self, eng):
        self.engine = eng
        if eng is None:
            return
        eng.push_handlers(self)
        eng.push_handlers(self.keys)
        self.tilesGroup.setMapSize(eng.getWidth() * TILESIZE, 
                                   eng.getHeight() * TILESIZE)
        
    def setRenderSize(self, width, height):
        self.renderWidth = width
        self.renderHeight = height
        
    def size(self, frame):
        super(CityView,self).size(frame)
    
    def layout(self, x, y):
        super(CityView,self).layout(x,y)
        self.tilesGroup.setViewportSize((self.width, self.height),
                                         (self.renderWidth, self.renderHeight))
        self.batch = self.savedFrame.batch
        if self.tileSprites is None:
            self._generateTileSprites()
        

    def reset(self, engine):
        '''
        To be called when city engine has changed, to update
        cityview to new engine.
        
        '''
        self._scrollX = 0
        self._scrollY = 0
        self.toolPreview = None
        
        self.deletePowerIndicators()
        self.deleteToolCursor()
        self._deleteTileSprites()
        
        self.setEngine(engine)
        if self.engine is not None:
            self._tileIndicators = create2dArray(
                                        self.engine.getWidth(), 
                                        self.engine.getHeight(), 
                                        None)
            
    def _deleteTileSprites(self):
        if self.tileSprites is not None:
            for y in xrange(self.mapHeight):
                for x in xrange(self.mapWidth):
                    if self.tileSprites[x][y] is not None:
                        self.tileSprites[x][y].delete()
                        self.tileSprites[x][y] = None
            self.tileSprites = None
            
    def deletePowerIndicators(self):
        if not self._tileIndicators:
            return
        for y in xrange(self.mapHeight):
            for x in xrange(self.mapWidth):
                if self._tileIndicators[x][y] is not None:
                    self._tileIndicators[x][y].delete()
                    self._tileIndicators[x][y] = None
        self._tileIndicators = None
    
    def _generateTileSprites(self):
        '''
        creates pyglet sprite objects for everytile
        at its static position. Stores in 2d list as member var
        '''
        if self.engine is None:
            return
        self.mapWidth = self.engine.getWidth()
        self.mapHeight = self.engine.getHeight()
        if self.tileSprites is not None:
            self._deleteTileSprites()
        self.tileSprites = create2dArray(self.mapWidth, self.mapHeight, None)
        for y in xrange(self.mapHeight):
            for x in xrange(self.mapWidth):
                cell = self.engine.getTile(x,y)
                x2 = (x * TILESIZE)
                y2 = (y * TILESIZE + TILESIZE)
                self.tileSprites[x][y] = TileSprite(cell,
                                    x2,
                                    y2,
                                    self.batch,
                                    self.tilesGroup,
                                    self.tileImages,
                                    self.animClock)
            

    def on_map_changed(self, tilesList):
        '''
        modifies tile batch with tilesList
        '''
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            cell = self.engine.getTile(x,y)
            self.tileSprites[x][y].setTile(cell)
     
    def on_power_indicator_changed(self, pos):
        x = pos[0]
        y = pos[1]
        ind = self.engine.getTileIndicator(x,y)
        if ind and self._tileIndicators[x][y]:
            self._tileIndicators[x][y].delete()
            self._tileIndicators[x][y] = None
        if ind:
            img = self.tileImages.getTileImage(tileConstants.LIGHTNINGBOLT)
            x2 = x * TILESIZE
            y2 = y * TILESIZE + TILESIZE
            self._tileIndicators[x][y] = Sprite(img,
                                                batch=self.batch,
                                                group=self.blinkingGroup,
                                                x=x2,
                                                y=y2)
        if not ind and self._tileIndicators[x][y] is not None:
            self._tileIndicators[x][y].delete()
            self._tileIndicators[x][y] = None
            

    
    def getHeight(self):
        return self.height
    
    def getWidth(self):
        return self.width
    
    def deleteToolCursor(self):
        if self.toolCursor is not None:
            self.toolCursor.vl.delete()
            self.toolCursor.borderVL.delete()
            self.toolCursor = None
            
    def setToolCursor(self, newCursor):
        '''
        
        '''
        if self.toolCursor is None\
            and self.toolCursor == newCursor:
            return
        
        self.deleteToolCursor()
        self.toolCursor = newCursor
        
        if self.toolCursor is not None:
            x,y,x2,y2 = self.expandMapCoords(self.toolCursor.rect)
            width = x2-x
            height = y2-y
            self.toolCursor.vl = createRect(x, y, width, height, 
                                            self.toolCursor.fillColor, 
                                            self.batch, 
                                            self.toolCursorGroup)
            self.toolCursor.borderVL = createHollowRect(x, y, width, height,
                                            self.toolCursor.borderColor, 
                                            self.batch, 
                                            self.toolCursorGroup)
            
        
    def newToolCursor(self, newRect, tool):
        '''
        
        '''
        if self.toolCursor and self.toolCursor.rect.equals(newRect):
            return
        
        newCursor = ToolCursor()
        newCursor.rect = newRect
        
        #tc.borderColor = (0, 200, 200)
        roadsBg = gui.config.get('tools.bgcolor', tool.name)
        newCursor.fillColor = map(int, tuple(roadsBg.split(',')))
        
        self.setToolCursor(newCursor)

    
    def setToolPreview(self, newPreview):
        '''
        Shows the given preview's tiles in place.
        If a preview already exists, resets those tiles.
        
        '''
        
        if self.toolPreview is not None:
            # reset old preview tile sprites
            b = self.toolPreview.getBounds()
            tilesList = list()
            for x in xrange(b.width):
                for y in xrange(b.height):
                    tilesList.append(
                                (x + b.x,
                                 y + b.y))
            self.on_map_changed(tilesList)
        
        if newPreview is not None:
            # set new preview tile sprites
            b = newPreview.getBounds()
            for y in xrange(b.height):
                for x in xrange(b.width):               
                    x2 = x - newPreview.offsetX
                    y2 = y - newPreview.offsetY
                    tNum = newPreview.getTile(x2,y2)
                    if tNum != CLEAR:
                        self.tileSprites[x2][y2].setTile(tNum)
        self.toolPreview = newPreview
        
        
    def expandMapCoords(self, rect):
        '''
            world-space coordinates of tile coord
        '''
        x = self.toolCursor.rect.x * TILESIZE
        y = (self.toolCursor.rect.y - 1) * TILESIZE + TILESIZE
        x2 = x + self.toolCursor.rect.width * TILESIZE
        y2 = y + self.toolCursor.rect.height * TILESIZE
        return (x,y,x2,y2)
        
    def screenCoordsToCityLocation(self, x, y):
        '''
        given window-space coords will return CityLocation object
        through tilesGroup
        '''
        return self.tilesGroup.screenCoordsToCityLocation(x, y)
        
    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.changeZoom(increment=1)
            self.tilesGroup.zoomToViewCenter = True
        if symbol == key.MINUS:
            self.changeZoom(increment=-1)
            self.tilesGroup.zoomToViewCenter = True
        if symbol == key._0:
            self.changeZoom(newValue=1.0)
            self.tilesGroup.zoomToViewCenter = True
            
    def changeZoom(self, newValue=None, increment=None):
        '''
            pass one value but not both. changeZoom increments
        '''
        assert newValue or increment and not (newValue and increment)
        
        if increment:
            self.tilesGroup.changeZoom(self.width/2, self.height/2, 
                                        -increment)
        else:
            self.tilesGroup.setZoom(self.width/2, self.height/2, 
                                        newValue)
        
            
    def zoomToPoint(self, x, y, change):
        self.tilesGroup.changeZoom(x, y, -change)
                
    def moveView(self, mx, my):
        self.tilesGroup.setFocus(mx, my)

            
    def setSpeed(self, speed):
        '''
        
        '''
        if speed == engine.speed.PAUSED:
            self.blinkingGroup.stop()
        else:
            self.blinkingGroup.start()
            
    def _checkScrollKeys(self, dt):
        # move 12 tiles per second
        delta = int(self.scrollSpeed * TILESIZE * dt) 
        if (self.keys[key.LEFT]):
            self.moveView(delta, 0)
        elif (self.keys[key.RIGHT]):
            self.moveView(-delta, 0)
        if (self.keys[key.DOWN]):
            self.moveView(0, delta)
        elif (self.keys[key.UP]):
            self.moveView(0, -delta)
            
    def update(self, dt):
        self._checkScrollKeys(dt)
        self.blinkingGroup.update(dt)
        self.tilesGroup.update(dt)
        
        
        
        
        
        
        
        