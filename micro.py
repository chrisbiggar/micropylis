'''
Created on Aug 29, 2015

@author: chris
'''
import imp, sys
import argparse
import pyglet
pyglet.options['debug_graphics_batch'] = False
pyglet.lib.load_library('avbin')
pyglet.have_avbin = True

'''
    Returns True if running from .exe
'''


def mainIsFrozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze


def doHighPriorityProcess():
    import os, psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)


if __name__ == '__main__':
    if mainIsFrozen():  # running from .exe
        skipToCity = 'kyoto.cty'
        disableSound = False
        pyglet.options['debug_gl'] = False

    else:  # running directly from python script
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug', dest='debugMode',
                            default=False, action="store_true")
        parser.add_argument('--disable-sound', dest='disableSound',
                            default=False, action="store_true")
        parser.add_argument('--print-to-file', dest='printToFile')
        parser.add_argument('--skip-to-city', dest='skipToCity')
        args = parser.parse_args()

        if args.printToFile:
            sys.stdout = open(args.printToFile, 'w')
        if not args.debugMode:
            pyglet.options['debug_gl'] = False
        skipToCity = args.skipToCity
        disableSound = args.disableSound

    # doHighPriorityProcess()
    from gui.microWindow import MicroWindow
    app = MicroWindow(skipToCity, not disableSound)
    pyglet.app.run()