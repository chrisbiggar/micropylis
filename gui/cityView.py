from random import randint

from pyglet.gl import *
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite
from pyglet.window import key

import layout
import microWindow
import gui
from gui import BG_RENDER_ORDER, MG_RENDER_ORDER, FG_RENDER_ORDER
from gui.speed import speeds
from gui.tileImageLoader import TileImageLoader
from tileMap import TileMapRenderer, TILESIZE

from engine import tileConstants
from engine.cityLocation import CityLocation
from engine.tileConstants import CLEAR

from util import create2dArray, createRect, createHollowRect



'''
    ViewportGroup

    Pyglet rendering group. Allows a zoomable and panable orthographic viewport to
    be controlled. Does not allows one to view outside defined map size.
    Gradually zooms in and out. Inverts opengl's screen bottom up coordinate sys
    so coords start at top and progress down.
'''


class ViewportGroup(OrderedGroup):
    INCREASE_ZOOM = 2
    DECREASE_ZOOM = 1
    LEFT = 1
    RIGHT = 2
    DOWN = 4
    UP = 8

    def __init__(self, order):
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

        self.focusTransition = None
        self.deltaX = 0
        self.deltaY = 0
        self.targetX = 0
        self.targetY = 0

        self.mapWidth = 0
        self.mapHeight = 0
        self.zoomedWidth = 0
        self.zoomedHeight = 0
        self.renderWidth = 0
        self.renderHeight = 0
        self.widgetWidth = 0
        self.widgetHeight = 0

        self.left = 0
        self.right = 0
        self.bottom = 0
        self.top = 0

    def setMapSize(self, width, height):
        self.mapWidth = width
        self.mapHeight = height

    '''
        Allows the render and widget sizes to be defined,
        recalculating the viewport accordingly.
    '''
    def setViewportSize(self, xxx_todo_changeme, xxx_todo_changeme1):
        (width, height) = xxx_todo_changeme
        (windowWidth, windowHeight) = xxx_todo_changeme1
        self.renderWidth = windowWidth
        self.renderHeight = windowHeight
        self.widgetWidth = width
        self.widgetHeight = height

        x = self.zoomX or (self.widgetWidth / 2)
        y = self.zoomY or (self.widgetHeight / 2)
        self._setZoom(x, y, None)

    def gotoSpot(self, x, y, zoom):
        self.setFocus(x, y)
        self._setZoom(0, 0, zoom)

    def changeFocus(self, dx, dy):
        self.setFocus(self.left - dx * self.zoomLevel,
                      self.bottom + dy * self.zoomLevel)

    '''
        setFocus

        Pans the view by the amount given in arguments,
        restricting the view within limits of map
    '''
    def setFocus(self, x, y):
        left = x
        bottom = y

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

        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top

    '''
        returns viewport with target_zoom factored in.
    '''
    def getViewport(self):
        newZoomLevel = self.targetZoom
        if not self.zoomX or not self.zoomY:
            self.zoomX = self.left + (self.widgetWidth/2)
            self.zoomY = self.bottom + (self.widgetHeight/2)

        mouseX = self.zoomX / float(self.renderWidth)
        mouseY = self.zoomY / float(self.renderHeight)

        mouseXInWorld = self.left + mouseX * self.zoomedWidth
        mouseYInWorld = self.bottom + mouseY * self.zoomedHeight

        zoomedWidth = self.renderWidth * newZoomLevel
        zoomedHeight = self.renderHeight * newZoomLevel

        left = int(mouseXInWorld - mouseX * zoomedWidth)
        right = int(mouseXInWorld + (1 - mouseX) * zoomedWidth)
        bottom = int(mouseYInWorld - mouseY * zoomedHeight)
        top = int(mouseYInWorld + (1 - mouseY) * zoomedHeight)

        return (int(left), int(bottom),
                int(right - left), int(top - bottom))

    '''
        sets an absolute zoom level,
            focused on x and y given in world-space coords.
        will not allow zoom < 0.2 or so far out that
        outside of map borders would be revealed.
    '''

    def _setZoom(self, x, y, newZoomLevel):
        if newZoomLevel is None:
            newZoomLevel = self.zoomLevel

        if .2 > newZoomLevel:
            ''' restricts zoom-in to a normal level '''
            return

        mouseX = x / float(self.renderWidth)
        mouseY = y / float(self.renderHeight)

        mouseXInWorld = self.left + mouseX * self.zoomedWidth
        mouseYInWorld = self.bottom + mouseY * self.zoomedHeight

        zoomedWidth = self.renderWidth * newZoomLevel
        zoomedHeight = self.renderHeight * newZoomLevel

        left = mouseXInWorld - mouseX * zoomedWidth
        right = mouseXInWorld + (1 - mouseX) * zoomedWidth
        bottom = mouseYInWorld - mouseY * zoomedHeight
        top = mouseYInWorld + (1 - mouseY) * zoomedHeight

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

    '''
        triggers a change in zoom level


        change = (newZoomLevel - self.zoomLevel)
        factor = 0.8 / abs(change)
    '''

    def setZoom(self, x, y, newZoomLevel, keepFocus=False):
        self.targetZoom = newZoomLevel
        self.zoomX = x
        self.zoomY = y
        self.keepFocus = keepFocus
        if newZoomLevel > self.zoomLevel:
            self.zoomTransition = self.INCREASE_ZOOM
            self.deltaZoom = 0.8
        elif newZoomLevel < self.zoomLevel:
            self.zoomTransition = self.DECREASE_ZOOM
            self.deltaZoom = -0.8

    '''
        allows zoom level to be changed incrementally
        by a predefined change factor.
        a negative dy will zoom out while a positive dy will zoom in.
    '''

    def changeZoom(self, x, y, dy):
        y = self.renderHeight - y

        # Get scale factor
        f = self.zoomInFactor if dy > 0 else self.zoomOutFactor if dy < 0 else 1

        newZoomLevel = self.zoomLevel * f
        self.setZoom(x, y, newZoomLevel)

    '''
        changes zoom at a gradual rate
    '''

    def updateZoomTransition(self, dt):
        if self.zoomTransition is not None:
            self._setZoom(self.zoomX, self.zoomY,
                          self.zoomLevel + self.deltaZoom * dt)
            if ((self.zoomTransition == self.INCREASE_ZOOM and
                         self.zoomLevel >= self.targetZoom) or
                    (self.zoomTransition == self.DECREASE_ZOOM and
                             self.zoomLevel <= self.targetZoom)):
                self.zoomTransition = None
                if self.keepFocus:
                    x = self.left
                    y = self.bottom
                    self._setZoom(self.zoomX, self.zoomY, self.targetZoom)
                    self.setFocus(x, y)
                else:
                    self._setZoom(self.zoomX, self.zoomY, self.targetZoom)

    def updateFocusTransition(self, dt):
        pass

    def update(self, dt):
        self.updateZoomTransition(dt)

    '''
        returns city relative location from gui coords
    '''
    def screenCoordsToCityLocation(self, x, y):
        y = self.renderHeight - y
        mouse_x = x / float(self.renderWidth)
        mouse_y = y / float(self.renderHeight)

        mouse_x_in_world = self.left + mouse_x * self.zoomedWidth
        mouse_y_in_world = self.bottom + mouse_y * self.zoomedHeight

        return CityLocation(int(mouse_x_in_world / TILESIZE),
                            int(mouse_y_in_world / TILESIZE))

    '''
        sets the viewport
    '''
    def set_state(self):
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

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.left == other.left and
                self.bottom == other.bottom and
                self.parent == other.parent)

    def __hash__(self):
        return hash((self.zoomSpeed, self.zoomInFactor))


'''
    BlinkingGroup

    Uses given class's state and adds a blink
    functionality.
'''


class BlinkingGroup(OrderedGroup):
    def __init__(self, order, viewportGroup=None):
        super(BlinkingGroup, self).__init__(order)
        self.blink = False
        self.lastChange = 0
        self.dt = 0
        self.freq = 0.8
        self.paused = False
        self.viewportGroup = viewportGroup

    def start(self):
        self.paused = False

    def stop(self):
        self.paused = True

    def update(self, dt):
        self.dt += dt
        if self.dt > self.lastChange + self.freq and not self.paused:
            self.blink = not self.blink
            self.lastChange = self.dt

    def set_state(self):
        self.viewportGroup.set_state()
        if self.blink:
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)

    def unset_state(self):
        self.viewportGroup.unset_state()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.blink == other.blink and
                self.parent == other.parent)

    def __hash__(self):
        return hash((int(55), 22))


class ToolCursorGroup(OrderedGroup):
    def __init__(self, order, viewportGroup):
        super(ToolCursorGroup, self).__init__(order)
        self.viewportGroup = viewportGroup

    def set_state(self):
        self.viewportGroup.set_state()

    def unset_state(self):
        self.viewportGroup.unset_state()

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.viewportGroup.left == other.viewportGroup.left and
                self.viewportGroup.bottom == other.viewportGroup.bottom and
                self.parent == other.parent)

    def __hash__(self):
        return hash((33, 256))


class ToolCursor(object):
    '''
    data structure for tool cursor visual
    '''

    def __init__(self):
        self.rect = None  # CityRect
        self.fillColor = None
        self.borderColor = (0, 0, 0, 255)
        self.vl = None
        self.borderVL = None








'''
class CityView

Controls the rendering of the city.
Provides panning and zoom through a ViewportGroup object.
'''


class CityView(layout.Spacer):
    def __init__(self, animClock):
        super(CityView, self).__init__()
        self.animClock = animClock
        self.tileImageLoader = TileImageLoader(
            gui.config.get('misc', 'TILES_FILE'),
            TILESIZE, flipTilesVert=True, padding=2)
        self.tbatch = pyglet.graphics.Batch()

        self.viewportGroup = ViewportGroup(BG_RENDER_ORDER)
        self.blinkingGroup = BlinkingGroup(MG_RENDER_ORDER, self.viewportGroup)
        self.toolCursorGroup = ToolCursorGroup(
            FG_RENDER_ORDER, self.viewportGroup)

        self.tileMapRenderer = TileMapRenderer(self.tileImageLoader, self.viewportGroup)

        self.tileSprites = None
        self.toolCursor = None
        self.toolPreview = None
        self.noPowerIndicators = None
        self.engine = None

        self.keys = microWindow.Keys(self)
        self.scrollSpeed = int(gui.config.get('misc', 'KEYBOARD_SCROLL_SPEED'))

    def setRenderSize(self, width, height):
        self.renderWidth = width
        self.renderHeight = height
        '''self.tileMapRenderer.setVisibleRegion(self.viewportGroup.left,self.viewportGroup.bottom,
                                              self.renderWidth, self.renderHeight)'''

    def size(self, frame):
        super(CityView, self).size(frame)

    def layout(self, x, y):
        super(CityView, self).layout(x, y)
        self.viewportGroup.setViewportSize(
            (self.width, self.height), (self.renderWidth, self.renderHeight))

    '''
        To be called when city engine has changed, to update
        cityview to new engine.

    '''

    def reset(self, eng):
        self.viewportGroup.setFocus(0, 0)
        self.toolPreview = None
        self.deletePowerIndicators()
        self.deleteToolCursor()

        self.engine = eng
        self.tileMapRenderer.reset(eng)

        if self.engine is not None:
            eng.push_handlers(self)
            self.mapWidth = eng.getWidth()
            self.mapHeight = eng.getHeight()
            self.viewportGroup.setMapSize(eng.getWidth() * TILESIZE,
                                          eng.getHeight() * TILESIZE)
            self.noPowerIndicators = create2dArray(
                self.engine.getWidth(),
                self.engine.getHeight(),
                None)

    def deletePowerIndicators(self):
        if not self.noPowerIndicators:
            return
        for y in xrange(self.mapHeight):
            for x in xrange(self.mapWidth):
                if self.noPowerIndicators[x][y] is not None:
                    self.noPowerIndicators[x][y].delete()
                    self.noPowerIndicators[x][y] = None
        self.noPowerIndicators = None

    '''
        modifies tile batch with tilesList
    '''

    def on_map_changed(self, tilesList):
        #if self.tileSprites is None:
            #return
        for tile in tilesList:
            x = tile[0]
            y = tile[1]
            cell = self.engine.getTile(x, y)
            #self.tileSprites[x][y].setTile(cell)
            self.tileMapRenderer.setTile(x, y, cell)


    def on_power_indicator_changed(self, pos):
        x = pos[0]
        y = pos[1]
        ind = self.engine.getTileIndicator(x, y)
        if ind and self.noPowerIndicators[x][y]:
            self.noPowerIndicators[x][y].delete()
            self.noPowerIndicators[x][y] = None
        if ind:
            img = self.tileImageLoader.getTileImage(
                tileConstants.LIGHTNINGBOLT)
            x2 = x * TILESIZE
            y2 = y * TILESIZE + TILESIZE
            self.noPowerIndicators[x][y] = Sprite(img,
                                                  batch=self.parentFrame.batch,
                                                  group=self.blinkingGroup,
                                                  x=x2,
                                                  y=y2)
        if not ind and self.noPowerIndicators[x][y] is not None:
            self.noPowerIndicators[x][y].delete()
            self.noPowerIndicators[x][y] = None

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
        if self.toolCursor is None \
                and self.toolCursor == newCursor:
            return

        self.deleteToolCursor()
        self.toolCursor = newCursor

        if self.toolCursor is not None:
            x, y, x2, y2 = self.expandMapCoords(self.toolCursor.rect)
            width = x2 - x
            height = y2 - y
            self.toolCursor.vl = createRect(x, y, width, height,
                                            self.toolCursor.fillColor,
                                            self.parentFrame.batch,
                                            self.toolCursorGroup)
            self.toolCursor.borderVL = createHollowRect(
                x,
                y,
                width,
                height,
                self.toolCursor.borderColor,
                self.parentFrame.batch,
                self.toolCursorGroup)

    def newToolCursor(self, newRect, tool):
        '''

        '''
        if self.toolCursor and self.toolCursor.rect.equals(newRect):
            return

        newCursor = ToolCursor()
        newCursor.rect = newRect

        # tc.borderColor = (0, 200, 200)
        roadsBg = gui.config.get('tools.bgcolor', tool.name)
        newCursor.fillColor = map(int, tuple(roadsBg.split(',')))

        self.setToolCursor(newCursor)

    '''
    Shows the given preview's tiles in place.
    If a preview already exists, resets those tiles.
    '''

    def setToolPreview(self, newPreview):
        return
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
                    tNum = newPreview.getTile(x2, y2)
                    if tNum != CLEAR:
                        self.tileSprites[x2][y2].setTile(tNum)
        self.toolPreview = newPreview

    '''
        world-space coordinates of tile coord
    '''

    def expandMapCoords(self, rect):
        x = self.toolCursor.rect.x * TILESIZE
        y = (self.toolCursor.rect.y - 1) * TILESIZE + TILESIZE
        x2 = x + self.toolCursor.rect.width * TILESIZE
        y2 = y + self.toolCursor.rect.height * TILESIZE
        return (x, y, x2, y2)

    '''
        given window-space coords will return CityLocation object
        through viewportGroup
    '''

    def screenCoordsToCityLocation(self, x, y):
        return self.viewportGroup.screenCoordsToCityLocation(x, y)

    def key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.changeZoom(increment=1)
        if symbol == key.MINUS:
            self.changeZoom(increment=-1)
        if symbol == key._0:
            self.changeZoom(newValue=1.0)
        if symbol == key.A:
            self.viewportGroup.gotoSpot(500, 400, 0.86)
        if symbol == key.I:
            self.tileMapRenderer.setTile(3, 3, 56)
        if symbol == key.O:
            self.engine.setTile(2, 2, 860)
            self.engine.tileUpdateCheck()
        if symbol == key.P:
            self.engine.setTile(2, 4, 860)
            self.engine.tileUpdateCheck()
        if symbol == key.L:
            self.engine.setTile(2, 6, 860)
            self.engine.tileUpdateCheck()
        if symbol == key.K:
            for x in xrange(60):
                for y in xrange(50):
                    self.engine.setTile(x, y, 56)
            self.engine.tileUpdateCheck()

    '''
        pass one value but not both. changeZoom increments
    '''
    def changeZoom(self, newValue=None, increment=None):
        assert newValue or increment and not (newValue and increment)

        if increment:
            self.viewportGroup.changeZoom(self.width / 2, self.height / 2,
                                          -increment)
        else:
            self.viewportGroup.setZoom(self.width / 2, self.height / 2,
                                       newValue)

        self.tileMapRenderer.setVisibleRegion(*self.viewportGroup.getViewport())



    def zoomToPoint(self, x, y, change):
        self.viewportGroup.changeZoom(x, y, -change)
        self.tileMapRenderer.setVisibleRegion(*self.viewportGroup.getViewport())

    def moveView(self, mx, my):
        self.viewportGroup.changeFocus(mx, my)
        #print self.viewportGroup.getViewport()
        self.tileMapRenderer.setVisibleRegion(*self.viewportGroup.getViewport())

    def setSpeed(self, speed):
        if speed == speeds['Paused']:
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
        self.viewportGroup.update(dt)
        self.tileMapRenderer.update(dt)
        '''t = randint(0,960)
        for x in xrange(74):
            for y in xrange(40):
                self.tileMapRenderer.setTile(x, y, t)'''

    def draw(self):
        #self.tbatch.draw()
        #return
        self.tileMapRenderer.draw()