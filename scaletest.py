'''
Created on Nov 27, 2015

@author: chris
'''

from pyglet.graphics import Group
from pyglet.window import key
from pyglet.gl import *

class Keys(pyglet.tilesView.key.KeyStateHandler):
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


class BgGroup(Group):
    def __init__(self, window):
        super(BgGroup, self).__init__()
        self.focusX = 0
        self.focusY = 0
        self._zoom = 1.0
        self.tilesView = window
        
    def setFocus(self, x=None, y=None):
        if x is not None:
            self.focusX = x
        if y is not None:
            self.focusY = y
            
    def setScale(self, newScale):
        self._zoom = newScale

    def set_state(self):
        glPushMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glTranslatef(float(self.focusX),float(self.focusY),0.)
        
        self.xOff = ((self.tilesView.width/2) * (1-self._zoom))
        self.yOff = (self.tilesView.height/2) * (1-self._zoom)
        
        xOff = -self.focusX + (self.tilesView.width/2)
        yOff = -self.focusY + (self.tilesView.height/2)
        glTranslatef(xOff,yOff,0.0)
        glScalef(self._zoom,self._zoom,1.0)
        glTranslatef(-xOff,-yOff,0.0)
        
        
    def unset_state(self):
        glPopMatrix()
    

class ScaleTestApp(pyglet.tilesView.Window):
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 660
    
    def __init__(self):
        super(ScaleTestApp,self).__init__(vsync=True)
        
        self.keys = Keys(self)
        self.push_handlers(self.keys)
        
        self.set_caption("Test Scale App")
        self.set_size(self.DEFAULT_WIDTH,self.DEFAULT_HEIGHT)
        self.set_location(20,20)
        self.group = BgGroup(self)
        
        self.scrollX = 0
        self.scrollY = 0
        self._zoom = 0
    
        bg = pyglet.image.load("res/testimg.png")
        self.bg = pyglet.sprite.Sprite(bg,x=0,y=0,group=self.group)
        
        pyglet.clock.schedule_interval(self.update, 1/60.)
        
    def on_resize(self, width, height):
        
        #self.initGLSettings(width, height)
        #return pyglet.event.EVENT_HANDLED
        pyglet.tilesView.Window.on_resize(self, width, height)
        
    
    def on_key_release(self, symbol, modifiers):
        if symbol == key.EQUAL:
            self.setZoom(increment=0.05)
        if symbol == key.MINUS:
            self.setZoom(increment=-0.05)
        if symbol == key.P:
            self.setZoom(newValue=1.0)
            

    def setZoom(self, newValue=None, increment=None):
        '''
            pass one value but not both. changeZoom increments
        '''
        assert newValue or increment and not (newValue and increment)
        
        if increment:
            newValue = self.group._zoom + increment
            
        if (self.bg.width >= self.width) and\
                (self.bg.height >= self.height):
            self._zoom = newValue
            print newValue
            self.group.setScale(self._zoom)
            #self.validateScroll()
        
            
    def on_mouse_motion(self, x, y, dx, dy):
        #print x,y
        pass
            
    def on_mouse_press(self, x, y, button, modifiers):
        pass
        
    def on_mouse_release(self, x, y, button, modifiers):
        
        if button == pyglet.tilesView.mouse.RIGHT:
            # screen coord to world coord (for tools)
            x = (x - self.group.xOff) / self.group._zoom + self.scrollX
            #print self.scrollX
            print y,self.group.yOff,self.scrollY,self.group._zoom
            y = self.height - (y - self.group.yOff) / self.group._zoom + self.scrollY 
            print x,y
    
    
    
    
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        #print self.scrollX,self.scrollY
        if buttons & pyglet.tilesView.mouse.LEFT:
            self.setScroll(-dx+self.scrollX,-dy+self.scrollY)
        
    def setScroll(self, x, y):
        
        # non restricted scrolling:
        '''self.scrollX = x
        self.scrollY = y
        self.group.setFocus(-self.scrollX, -self.scrollY)
        print self.scrollX,self.scrollY
        return'''
        
        maxX = self.bg.width / self.group._zoom - self.width
        minX = self.group.xOff
        maxX = minX + maxX 
        self.scrollX = max(minX,x)
        self.scrollX = min(maxX,self.scrollX)
        
        maxY = self.bg.height - self.height
        minY = self.group.yOff / self.group._zoom
        maxY = minY + maxY
        self.scrollY = max(minY,y)
        self.scrollY = min(maxY,self.scrollY)
        print self.scrollX,self.scrollY
        self.group.setFocus(-self.scrollX, -self.scrollY)
    
    def _checkScrollKeys(self, dt):
        # move 12 tiles per second
        delta = 12
        if (self.keys[key.LEFT]):
            self.setScroll(-delta+self.scrollX, self.scrollY)
        elif (self.keys[key.RIGHT]):
            self.setScroll(delta+self.scrollX, self.scrollY)
        if (self.keys[key.DOWN]):
            self.setScroll(self.scrollX,delta+self.scrollY)
        elif (self.keys[key.UP]):
            self.setScroll(self.scrollX,-delta+self.scrollY)
        
    def update(self, dt):
        self._checkScrollKeys(dt)

    
    def on_draw(self):
        self.clear()
        self.bg.draw()

if __name__ == '__main__':
    app = ScaleTestApp()
    pyglet.app.run()