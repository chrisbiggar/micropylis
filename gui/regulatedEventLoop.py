'''
Created on Jan 24, 2016

@author: chris
'''
import pyglet
from pyglet import clock


class RegulatedEventLoop(pyglet.app.base.EventLoop):
    '''
    Custom pyglet event loop that allows control over speed.
    By setting an animation coefficient
    '''
    def __init__(self):
        super(RegulatedEventLoop,self).__init__()
        self.animCoefficient = 0
        self.animClock = clock.Clock(time_function=self.getTime)
        
    def idle(self):
        dt = self.clock.update_time()
        self.animClock.update_time()
        self.animClock.call_scheduled_functions(dt)
        return super(RegulatedEventLoop,self).idle()
    
    def setSpeed(self, lastSpeed, newSpeed):
        '''
        
        Parameters:
        lastSpeed the last speed obj so cityview can save lastTs
        newSpeed the new newSpeed to set
        '''
        if lastSpeed:
            lastSpeed.lastTs = self.getTime()
        self.animClock.restore_time(newSpeed.lastTs)
        self.animCoefficient = newSpeed.animCoefficient
    
    def getTime(self):
        ''' dilates time for controlling animation clock speed'''
        return clock._default_time_function() * self.animCoefficient
    
    def getClock(self):
        return self.animClock