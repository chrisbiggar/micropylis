
import ConfigParser
import math
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
import kytten
from viewingPane import ViewingPane
from engine import Engine, micropolistool
import engine.micropolistool
from engine.micropolistool import MicropylisTool
from engine.cityRect import CityRect
import dialogs
from engine.toolResult import ToolResult
from infoPane import InfoPane


'''  '''
config = ConfigParser.ConfigParser()
config.read('res/gui.cfg')

cityMessages = ConfigParser.ConfigParser()
cityMessages.read('res/citymessages.cfg')

'''
class MainWindow

The main window for micropylis
'''
class MainWindow(pyglet.window.Window):
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 660
    
    def __init__(self):
        super(MainWindow, self).__init__(vsync=True)
        
        engine.tiles.Tiles().readTiles() # load in tile specs
        self.engine = Engine()
        # load test map:
        self.engine.loadCity('cities/hawkins.cty')
        
        # tool vars:
        self.dragStart = (0,0)
        self.currentTool = None
        self.toolStroke = None
        self.lastX = 0
        self.lastY = 0
        
        # window stuff
        self.initGLSettings()
        self.set_caption("Micropylis")
        self.set_icon(pyglet.image.load("res/icon32.png"))
        self.set_size(self.DEFAULT_WIDTH,self.DEFAULT_HEIGHT)
        self.set_location(40,40)
        self.fpsDisplay = self.fpsDisplay = pyglet.clock.ClockDisplay()
        self.initGuiComponents()
        
        pyglet.clock.schedule_interval(self.update, 1/60.)
        
        #testing sounds:
        #music = pyglet.media.load('explosion.wav'
        
    def initGuiComponents(self):
        self.setupDialogs()
        
        vPWidth = math.floor(self.DEFAULT_WIDTH * 0.75)
        self.viewingPane = ViewingPane(self.engine, 0, 0,
                                    vPWidth, self.DEFAULT_HEIGHT)
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
        
    def initGLSettings(self):
        # GL_NEAREST rendering for zoomed scale without seams between tiles:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glEnable(GL_BLEND)
        
    def on_key_release(self, symbol, modifiers):
        if (symbol == pyglet.window.key.X):
            self.engine.testChange()
            
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
        self.viewingPane.setSize(math.floor(self.DEFAULT_WIDTH * 0.75), 
                                    height)
        pyglet.window.Window.on_resize(self, width, height)
        
    def on_close(self):
        #self.viewingPane.cleanup()
        return super(MainWindow,self).on_close()
    
    def selectTool(self, toolType):
        if self.currentTool is not None and \
                toolType == self.currentTool.name:
            return
        
        tool = MicropylisTool.factory(toolType)
        
        self.currentTool = tool
        
        # cost?
        
    
    def onToolDown(self, x, y, button, modifiers):
        if button == mouse.RIGHT:
            loc = self.viewingPane.evToCityLocation(x, y)
            self.doQueryTool(loc.x, loc.y)
            return

        if button != mouse.LEFT:
            return
        
        if self.currentTool == None:
            return
        
        loc = self.viewingPane.evToCityLocation(x, y)
        
        if self.currentTool.type == engine.micropolistool.QUERY:
            self.doQueryTool(loc.x, loc.y)
            self.toolStroke = None
        else:
            self.toolStroke = self.currentTool.beginStroke(
                                                self.engine,
                                                loc.x, loc.y)
            self.previewTool()
            
        self.lastX = loc.x
        self.lastY = loc.y
        

        
    def onToolDrag(self, x, y, dx, dy, buttons, modifiers):
        if not self.viewingPane.withinRange(self.dragStart[0], self.dragStart[1]):
            return
        
        if self.currentTool is None:
            # pan view
            self.viewingPane.moveView(-dx, dy)
            return
        if buttons & mouse.LEFT == 0:
            return
        
        loc = self.viewingPane.evToCityLocation(x, y)
        tx = loc.x
        ty = loc.y
        if tx == self.lastX and ty == self.lastY:
            return
        
        if self.toolStroke is not None:
            self.toolStroke.dragTo(tx, ty)
            self.previewTool()
        elif self.currentTool == micropolistool.QUERY:
            self.doQueryTool(tx, ty)
        
        self.lastX = tx
        self.lastY = ty
        
        
    def onToolUp(self, x, y, button, modifiers):
        if self.toolStroke is not None:
            self.viewingPane.setToolPreview(None)
            self.showToolResult(self.toolStroke.getLocation(),
                                self.toolStroke.apply())
            self.toolStroke = None
            
        self.onToolHover(x,y)
        
        #TODO conditionally show budget window
        
            
    def onToolHover(self, x, y):
        if self.currentTool is None or\
            self.currentTool.type == engine.micropolistool.QUERY:
                self.viewingPane.setToolCursor2(None)
                return
            
        loc = self.viewingPane.evToCityLocation(x,y)
        x = loc.x
        y = loc.y
        w = self.currentTool.getWidth()
        h = self.currentTool.getHeight()
        
        if w >= 3:
            x -= 1
        if h >= 3:
            y -= 1
        
        rect = CityRect(x,y,w,h)
        self.viewingPane.setToolCursor(rect, self.currentTool)
        
    def previewTool(self):
        assert self.toolStroke is not None
        assert self.currentTool is not None
        
        self.viewingPane.setToolCursor(self.toolStroke.getBounds(), 
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
        queryMsg = "Tile Value of ({0},{1}): {2}".format(
                str(xPos), str(yPos), str(tileValue))
        self.infoPane.addInfoMessage(queryMsg)
    
    def update(self,dt):
        self.engine.animate()
        self.viewingPane.update(dt)
        self.infoPane.update(dt)
        
    def updateKytten(self, dt):
        self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        self.viewingPane.tileBatch.draw()
        if self.viewingPane.toolCursor is not None:
            self.viewingPane.toolCursor.vl.draw(GL_QUADS)
        self.infoPane.batch.draw()
        self.dialogBatch.draw()
        self.fpsDisplay.draw()