'''
Created on Aug 29, 2015

@author: chris
'''
import imp, sys, os
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
    import psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)


if __name__ == '__main__':
    if mainIsFrozen():  # running from .exe
        skipToCity = None
        disableSound = False
        pyglet.options['debug_gl'] = False
        printToFile = "micro_log_"

    else:  # running directly from python script
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug', dest='debugMode',
                            default=False, action="store_true")
        parser.add_argument('--disable-sound', dest='disableSound',
                            default=False, action="store_true")
        parser.add_argument('--print-to-file', dest='printToFile')
        parser.add_argument('--skip-to-city', dest='skipToCity')
        args = parser.parse_args()

        if not args.debugMode:
            pyglet.options['debug_gl'] = False
        skipToCity = args.skipToCity
        disableSound = args.disableSound
        printToFile = args.printToFile

    if printToFile:
            logFile = printToFile + "0"
            n = 1
            while os.path.isfile(logFile):
                logFile = printToFile + str(n)
                n += 1
            sys.stdout = open(logFile, 'w')

    from gui.microWindow import MicroWindow
    app = MicroWindow(skipToCity, not disableSound)
    pyglet.app.run()