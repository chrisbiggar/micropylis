
import pyglet
from pyglet.gl import *
import kytten
from viewingPane import ViewingPane
from engine import Engine
import dialogs




'''
class MainWindow

The main window for micropylis
'''
class MainWindow(pyglet.window.Window):
    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 680
    
    def __init__(self):
        super(MainWindow, self).__init__(vsync=True)
        self.engine = Engine()
        self.set_caption("Micropylis")
        self.set_icon(pyglet.image.load("res/icon32.png"))
        self.set_size(self.DEFAULT_WIDTH,self.DEFAULT_HEIGHT)
        self.set_location(40,40)
        self.fpsDisplay = self.fpsDisplay = pyglet.clock.ClockDisplay()
        
        # test map:
        self.engine.loadCity('cities/kyoto.cty')
        
        self.viewingPane = ViewingPane(self.engine, 
                                    self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.push_handlers(self.viewingPane.keys)
        pyglet.clock.schedule_interval(self.update, 1/60.)
        self.dialogBatch = pyglet.graphics.Batch()
        self.mainDialog = dialogs.MainDialog(self)
        self.register_event_type('on_update')
        self.push_handlers(self.mainDialog)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        self.initGLSettings()
        
    def initGLSettings(self):
        # GL_NEAREST rendering for zoomed scale without seams between tiles:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        
    def on_key_release(self, symbol, modifiers):
        if (symbol == pyglet.window.key.X):
            self.engine.testChange()
            
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
            # mouse handlers will call active tool methods
            
            # pan tool function:
            self.viewingPane.moveView(-dx, dy)
        
    def on_resize(self, width, height):
        self.viewingPane.setSize(width, height)
        pyglet.window.Window.on_resize(self, width, height)
        
    def on_close(self):
        #self.viewingPane.cleanup()
        return super(MainWindow,self).on_close()
    
    def update(self,dt):
        self.engine.animate()
        self.viewingPane.update(dt)
        
    def updateKytten(self, dt):
        self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        self.viewingPane.tileBatch.draw()
        self.dialogBatch.draw()
        self.fpsDisplay.draw()