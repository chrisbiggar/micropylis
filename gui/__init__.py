
import ConfigParser
import math
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
import kytten
import engine
from engine import Engine, micropolistool, speed, tiles, tileConstants
from engine.micropolistool import MicropylisTool
from engine.cityRect import CityRect
from viewingPane import ViewingPane
import dialogs
from engine.toolResult import ToolResult
from infoPane import InfoPane
from gui.dialogs import NewCityDialog


'''  '''
config = ConfigParser.ConfigParser()
config.read('res/gui.cfg')

cityMessages = ConfigParser.ConfigParser()
cityMessages.read('res/citymessages.cfg')




class Keys(pyglet.window.key.KeyStateHandler):
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



'''
class MainWindow

The main window for micropylis
'''
class MainWindow(pyglet.window.Window):
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 660
    
    def __init__(self):
        super(MainWindow, self).__init__(width=self.DEFAULT_WIDTH,
                                         height=self.DEFAULT_HEIGHT,
                                         resizable=True,
                                         vsync=True)
        
        tiles.Tiles().readTiles() # load in tile specs
        
        # load test map:
        self.newCity()
        #self.loadCity('cities/hawkins.cty')
        
        # tool vars:
        self.dragStart = (0,0)
        self.currentTool = None
        self.toolStroke = None
        self.lastX = 0
        self.lastY = 0
        
        # window stuff
        self.set_minimum_size(640, 480)
        self.set_caption("Micropylis")
        self.set_icon(pyglet.image.load("res/icon32.png"))
        self.set_location(40,40)
        self.fpsDisplay = pyglet.clock.ClockDisplay(color=(.2,.2,.2,0.6))
        self.initGuiComponents()

        pyglet.clock.schedule_interval(self.update, 1/60.)
        self.speed = None
        self.setSpeed(speed.PAUSED)
        
        #testing sounds:
        #music = pyglet.media.load('explosion.wav
        
    def setExitFunc(self, func):
        self.exitFunc = func
        
    def newCity(self):
        #newCityDialog = NewCityDialog(self)
        
        self.engine = Engine()
        
    
    def loadCity(self, filePath):
        self.engine = Engine()
        self.engine.loadCity(filePath)
        
    def initGuiComponents(self):
        self.setupDialogs()
        
        vPWidth = math.floor(self.DEFAULT_WIDTH * 0.75)
        self.viewingPane = ViewingPane(self.engine, 0, 0,
                                    vPWidth, self.DEFAULT_HEIGHT)
        self.engine.push_handlers(self.viewingPane)
        self.push_handlers(self.viewingPane.keys)
        
        self.infoPane = InfoPane(self.engine,  
                                 self.viewingPane.getWidth() + 1, 0, 
                                 self.DEFAULT_WIDTH - self.viewingPane.getWidth(),
                                  self.DEFAULT_HEIGHT)
        self.engine.push_handlers(self.infoPane)
        
    def setupDialogs(self):
        self.dialogBatch = pyglet.graphics.Batch()
        self.mainDialog = dialogs.ToolDialog(self)
        self.register_event_type('on_update')
        self.push_handlers(self.mainDialog)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        
    def toggleFullscreen(self):
        if not self._fullscreen:
            self.set_fullscreen(True)
        else:
            self.set_fullscreen(False)
        
    def on_key_release(self, symbol, modifiers):
        if (symbol == pyglet.window.key.X):
            self.engine.testChange()
        elif (modifiers & pyglet.window.key.MOD_ALT and
                symbol == pyglet.window.key.ENTER):
            self.toggleFullscreen()
        elif symbol == pyglet.window.key._1:
            self.setSpeed(speed.PAUSED)
        elif symbol == pyglet.window.key._2:
            self.setSpeed(speed.SLOW)
        elif symbol == pyglet.window.key._3:
            self.setSpeed(speed.NORMAL)
        elif symbol == pyglet.window.key._4:
            self.setSpeed(speed.FAST)
        elif symbol == pyglet.window.key._5:
            self.setSpeed(speed.SUPER_FAST)
            
    def on_mouse_motion(self, x, y, dx, dy):
        #pyglet.window.Window.on_resize(self, x, y, dx, dy)
        if self.viewingPane.withinRange(x, y):
            self.onToolHover(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        self.dragStart = (x,y)
        if self.viewingPane.withinRange(x, y):
            self.onToolDown(x, y, button, modifiers)
        
    def on_mouse_release(self, x, y, button, modifiers):
        if self.viewingPane.withinRange(x, y):
            self.onToolUp(x, y, button, modifiers)
            
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.viewingPane.withinRange(x, y):
            self.onToolDrag(x, y, dx, dy, buttons, modifiers)
        
    def on_resize(self, width, height):
        self.viewingPane.resize(math.floor(self.DEFAULT_WIDTH * 0.75), 
                                    height)
        self.infoPane.resize(self.viewingPane.getWidth() + 1, 0, width, height)
        super(MainWindow,self).on_resize(width, height)

        
    def on_close(self):
        #self.viewingPane.cleanup()
        self.exitFunc()
        return super(MainWindow,self).on_close()
    
    
    '''
        selectTool(tooltype)
        accepts a string specifying what tool should
        be currently active. returns tool type object
    '''
    def selectTool(self, toolType):
        if self.currentTool is not None and \
                toolType == self.currentTool.name:
            return
        if toolType == "Pan":
            self.currentTool = None
            return
        
        tool = MicropylisTool.factory(toolType)
        self.currentTool = tool
        return tool
        
    
    def onToolDown(self, x, y, button, modifiers):
        loc = self.viewingPane.evToCityLocation(x, y)
        self.lastX = loc.x
        self.lastY = loc.y
        #print self.lastX
        #print x,y
        if button == mouse.RIGHT:
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_CROSSHAIR))
            return
        if self.currentTool == None:
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_CROSSHAIR))
            return
        if button != mouse.LEFT:
            return
        if self.currentTool.type == micropolistool.QUERY:
            self.doQueryTool(loc.x, loc.y)
            self.toolStroke = None
        else:
            self.toolStroke = self.currentTool.beginStroke(
                                                self.engine,
                                                loc.x, loc.y)
            self.previewTool()
            self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_HAND))
            
        
    def onToolDrag(self, x, y, dx, dy, buttons, modifiers):
        if not self.viewingPane.withinRange(self.dragStart[0], self.dragStart[1]):
            return
        if self.currentTool is None or\
                buttons & mouse.RIGHT:
            self.viewingPane.moveView(dx, dy)
            return
        loc = self.viewingPane.evToCityLocation(x, y)
        tx = loc.x
        ty = loc.y
        if tx == self.lastX and ty == self.lastY:
            return
        if buttons & mouse.LEFT == 0:
            return
        self.lastX = tx
        self.lastY = ty
        if self.toolStroke is not None:
            self.toolStroke.dragTo(tx, ty)
            self.previewTool()
        elif self.currentTool == micropolistool.QUERY:
            self.doQueryTool(tx, ty)
        
        
    def onToolUp(self, x, y, button, modifiers):
        if self.toolStroke is not None:
            self.viewingPane.setToolPreview(None)
            self.showToolResult(self.toolStroke.getLocation(),
                                self.toolStroke.apply())
            self.toolStroke = None
            self.engine.tileUpdateCheck()
        #print x,y
        loc = self.viewingPane.evToCityLocation(x, y)
        tx = loc.x
        ty = loc.y
        #print self.lastX,tx
        if button == mouse.RIGHT and self.lastX == tx and self.lastY == ty:
            self.doQueryTool(tx, ty)
        self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_DEFAULT))    
        self.onToolHover(x,y)
        #TODO conditionally show budget window here?
        
            
    def onToolHover(self, x, y):
        if self.currentTool is None or\
            self.currentTool.type == micropolistool.QUERY:
                self.viewingPane.setToolCursor(None)
                return
            
        loc = self.viewingPane.evToCityLocation(x,y)
        #print loc
        x = loc.x
        y = loc.y
        w = self.currentTool.getWidth()
        h = self.currentTool.getHeight()
        
        if w >= 3:
            x -= 1
        if h >= 3:
            y -= 1
        
        rect = CityRect(x,y,w,h)
        self.viewingPane.newToolCursor(rect, self.currentTool)
        
    def previewTool(self):
        assert self.toolStroke is not None
        assert self.currentTool is not None
        
        self.viewingPane.newToolCursor(self.toolStroke.getBounds(), 
                                        self.currentTool)
        self.viewingPane.setToolPreview(self.toolStroke.getPreview())
        
    def showToolResult(self, loc, result):
        if result.value == ToolResult.SUCCESS:
            formatString = cityMessages.get('toolresults','SUCCESS')
            msg = formatString.format(cost=str(result.cost))
            self.infoPane.addInfoMessage(msg)
        elif result.value == ToolResult.INSUFFICIENT_FUNDS:
            self.infoPane.addInfoMessage(
                            cityMessages.get('toolresults','INSUFFICIENT_FUNDS'))
        elif result.value == ToolResult.UH_OH:
            self.infoPane.addInfoMessage(
                            cityMessages.get('toolresults','BULLDOZE_FIRST'))
        elif result.value == ToolResult.NONE:
            self.infoPane.addInfoMessage(
                            cityMessages.get('toolresults','NONE'))
        
    
    def doQueryTool(self, xPos, yPos):
        ''' print tilevalue to infopane messages '''
        tileValue = self.engine.getTile(xPos,yPos)
        self.engine.setTile(xPos,yPos,tileConstants.WOODS)
        return
        queryMsg = "Power of ({0},{1}): {2}".format(
                str(xPos), str(yPos), str(self.engine.hasPower(xPos, yPos)))
        '''queryMsg = "Power of ({0},{1}): {2}".format(
                str(xPos), str(yPos), str(self.engine.getTile(xPos, yPos)))'''
        self.infoPane.addInfoMessage(queryMsg)
        
    def setSpeed(self, newSpeed):
        if newSpeed == self.speed:
            return
        pyglet.clock.unschedule(self.engine.animate)
        self.viewingPane.setSpeed(self.speed, newSpeed)
        self.speed = newSpeed
        self.infoPane.addInfoMessage(newSpeed.name + " Speed")
        if self.speed == speed.PAUSED:
            return
        pyglet.clock.schedule_interval(self.engine.animate, newSpeed.delay)

        
        
    def update(self, dt):
        self.viewingPane.update(dt)
        self.infoPane.update(dt)
        
    def updateKytten(self, dt):
        self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        #pyglet.gl.glClearColor(240,240,240,255)
        self.clear()
        self.viewingPane.batch.draw()
        self.infoPane.batch.draw()
        self.dialogBatch.draw()
        self.fpsDisplay.draw()