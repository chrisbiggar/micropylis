'''
Created on Aug 29, 2015

@author: chris
'''
import pyglet
import gui
from gui import viewingPane

class MicroEventLoop(pyglet.app.base.EventLoop):
    def __init__(self, viewingPane):
        super(MicroEventLoop,self).__init__()
        self.viewingPane = viewingPane
        
    def idle(self):
        dt = self.clock.update_time()
        if self.viewingPane.animClock:
            self.viewingPane.animClock.update_time()
            self.viewingPane.animClock.call_scheduled_functions(dt)
        return super(MicroEventLoop,self).idle()


if __name__ == '__main__':
    app = gui.MainWindow()
    eventLoop = MicroEventLoop(app.viewingPane)
    app.setExitFunc(eventLoop.exit)
    eventLoop.run()