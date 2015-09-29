
import pyglet
import kytten
from viewingPane import ViewingPane
from engine import Engine
import dialogs

'''
class MainWindow

The main window for micropylis
'''
class MainWindow(pyglet.window.Window):
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 640
    
    def __init__(self):
        super(MainWindow, self).__init__(vsync=False)
        self.engine = Engine()
        self.set_caption("Micropylis")
        self.set_size(self.DEFAULT_WIDTH,self.DEFAULT_HEIGHT)
        self.set_location(40,40)
        self.fpsDisplay = self.fpsDisplay = pyglet.clock.ClockDisplay()
        self.viewingPane = ViewingPane(self.engine, self.width, self.height)
        self.push_handlers(self.viewingPane.keys)
        pyglet.clock.schedule_interval(self.update, 1/60.)
        self.batch = pyglet.graphics.Batch()
        self.dialogBatch = pyglet.graphics.Batch()
        self.mainDialog = dialogs.MainDialog(self)
        self.register_event_type('on_update')
        self.push_handlers(self.mainDialog)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        
        
    def on_resize(self, width, height):
        self.viewingPane.setSize(width, height)
        pyglet.window.Window.on_resize(self, width, height)
            
    def on_close(self):
        #self.viewingPane.cleanup()
        return super(MainWindow,self).on_close()
    
    def update(self,dt):
        self.viewingPane.update(dt)
        self.engine.step()
        
    def updateKytten(self, dt):
        self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        self.viewingPane.tileBatch.draw()
        self.dialogBatch.draw()
        self.fpsDisplay.draw()