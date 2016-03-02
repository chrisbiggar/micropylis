'''
Created on Aug 29, 2015

@author: chris
'''
import argparse
import pyglet
pyglet.options['debug_graphics_batch'] = False
pyglet.lib.load_library('avbin')
pyglet.have_avbin = True


def doHighPriorityProcess():
    import os, psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debugMode',
                        default=False, action="store_true")
    parser.add_argument('--disable-sound', dest='disableSound',
                        default=False, action="store_true")
    parser.add_argument('--print-to-file', dest='printToFile')
    parser.add_argument('--skip-to-city', dest='skipToCity')
    args = parser.parse_args()

    if args.printToFile:
        import sys
        sys.stdout = open(args.printToFile, 'w')

    if not args.debugMode:
        pyglet.options['debug_gl'] = False

    # doHighPriorityProcess()

    from gui.microWindow import MicroWindow
    app = MicroWindow(args.skipToCity, not args.disableSound)
    pyglet.app.run()