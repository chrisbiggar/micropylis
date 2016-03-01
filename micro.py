'''
Created on Aug 29, 2015

@author: chris
'''
import pyglet
pyglet.lib.load_library('avbin')
pyglet.have_avbin = True
pyglet.options['debug_gl'] = True
pyglet.options['debug_graphics_batch'] = False

from gui.microWindow import MicroWindow

'''import sys
sys.stdout = open('debugbatch.txt', 'w')'''

if __name__ == '__main__':
    '''import os, psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)'''

    app = MicroWindow()
    pyglet.app.run()