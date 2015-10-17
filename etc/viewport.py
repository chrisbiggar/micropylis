
import pyglet
from pyglet.graphics import OrderedGroup
from pyglet.gl import glEnable, glViewport, glMatrixMode, glLoadIdentity, glBlendFunc, \
    gluPerspective, gluLookAt, GL_PROJECTION, GL_MODELVIEW, GL_BLEND, \
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, glClearColor, glTranslatef, \
    glColorMask, GL_FALSE, GL_TRUE
import kytten


'''
    Object Layer
'''
class DisplayGroup(OrderedGroup):
    def __init__(self):
        super(DisplayGroup, self).__init__(1)
        self.focusX = 0
        self.focusY = 0
        
    def setFocus(self, x, y):
        self.focusX = x
        self.focusY = y

    def set_state(self):
        glTranslatef(self.focusX, self.focusY, 0)
        #glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        pass
        
    def unset_state(self):
        glTranslatef(-self.focusX, -self.focusY, 0)
        #glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        pass

'''
class MainWindow

The main window for micropylis
'''
class MainWindow(pyglet.window.Window):
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 640
    
    def __init__(self):
        super(MainWindow, self).__init__(vsync=False)
        self.set_caption("Viewport test")
        self.set_size(self.DEFAULT_WIDTH,self.DEFAULT_HEIGHT)
        self.set_location(40,40)
        self.fpsDisplay = self.fpsDisplay = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(self.update, 1/60.)
        self.batch = pyglet.graphics.Batch()
        self.group = DisplayGroup()
        img = pyglet.image.load("airport.png")
        self.sprite = pyglet.sprite.Sprite(img, x=200, y=200,
                                        batch=self.batch, group=self.group)
        
        
    def on_resize(self, width, height):
        return self.setViewport(width,height)
        
        
    def setViewport(self, width, height):
        '''
        calculate perspective matrix
        '''
        v_ar = width/float(height)
        usableWidth = int(min(width, height*v_ar))
        usableHeight = int(min(height, width/v_ar))
        ox = (width - usableWidth) // 2
        oy = (height - usableHeight) // 2
        glViewport(ox, oy, usableWidth, usableHeight)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, usableWidth/float(usableHeight), 0.1, 3000.0)
        ''' set camera position on modelview matrix
        '''
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(width/2.0, height/2.0, height/1.1566,
            width/2.0, height/2.0, 0,
            0.0, 1.0, 0.0)
        ''' update scene controller with size
        '''
        #clears to a grey.
        #glClearColor(0.4,0.4,0.4,0.)
        return pyglet.event.EVENT_HANDLED
            
    def on_close(self):
        #self.viewingPane.cleanup()
        return super(MainWindow,self).on_close()
    
    def update(self,dt):
        pass
        
    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.fpsDisplay.draw()
        
if __name__ == '__main__':
    app = MainWindow()
    pyglet.app.run()