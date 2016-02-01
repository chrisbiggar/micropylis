'''
Created on Aug 29, 2015

@author: chris
'''
''''import pyglet
pyglet.options['debug_gl'] = False'''
from gui.microWindow import MicroWindow
from gui.regulatedEventLoop import RegulatedEventLoop



if __name__ == '__main__':
    #import os
    #os.nice(-20)
    #import os, psutil
    #p = psutil.Process(os.getpid())
    #p.nice(psutil.HIGH_PRIORITY_CLASS)
    
    eventLoop = RegulatedEventLoop()
    app = MicroWindow(eventLoop)
    eventLoop.run()