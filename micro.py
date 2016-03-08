'''
Created on Aug 29, 2015

@author: chris
'''
import imp, sys, os, shutil, logging, tempfile
import argparse
import pyglet
pyglet.options['debug_graphics_batch'] = False


tempDir = os.path.join(tempfile.gettempdir(), "micropylis")


def mainIsFrozen():
    '''
        Returns True if running from .exe
    '''
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze


def doHighPriorityProcess():
    import psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)


def unpackResources(zipName, tempResDir):
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir)
    os.mkdir(tempDir)
    import zipfile
    zipFile = zipfile.ZipFile(zipName)
    zipFile.extractall(tempDir)


def checkResources(zipName, tempDir):
    '''
        Unpacks resources if zipped.
        returns True if resources are unpacked from zip.
    '''
    if os.path.isfile(zipName):
        unpackResources(zipName, tempDir)
        return True
    else:
        return False


def releaseAvbin():
    '''
    Frees Avbin .dll so windows will allow it to be deleted

    :return:
    '''
    def deleteLib(daLib):
        from _ctypes import FreeLibrary
        hlib = daLib._handle
        del daLib
        FreeLibrary(hlib)

    from pyglet.media import avbin
    deleteLib(avbin.av)
    deleteLib(avbinLib)


def initLogger(logFile=None, overwrite=False, level=logging.INFO):
    fileName = None
    if logFile:
        if overwrite:
            fileName = logFile
        else:
            fileName = logFile + "0"
            n = 1
            while os.path.isfile(fileName):
                fileName = logFile + str(n)
                n += 1
        logHandler = logging.FileHandler(fileName)
    elif logFile is None:
        logHandler = logging.StreamHandler(sys.stdout)

    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(level=level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logHandler.setFormatter(formatter)

    logger.addHandler(logHandler)

    return fileName


def deleteLogFileIfEmpty(fileName):
    '''
    Closes logger handlers and deletes logfile if empty

    :param fileName:
    :return:
    '''
    logger = logging.getLogger(__name__)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    if logFileName is not None and os.path.isfile(logFileName):
        if os.stat(logFileName).st_size == 0:
            os.remove(logFileName)


if __name__ == '__main__':
    if mainIsFrozen():  # running from .exe
        skipToCity = None
        disableSound = False
        pyglet.options['debug_gl'] = False
        logFile = "micro_log_"
        loggingLevel = logging.ERROR
        overwriteLogFile = False

    else:  # running directly from python script
        parser = argparse.ArgumentParser()
        parser.add_argument('-d', '--debug-gl', dest='debugGl',
                            default=False, action="store_true")
        parser.add_argument('--log-file', dest='logFile',
                            default=None)
        parser.add_argument('--log-level', dest='logLevel',
                            default='ERROR')
        parser.add_argument('--disable-sound', dest='disableSound',
                            default=False, action="store_true")
        parser.add_argument('--skip-to-city', dest='skipToCity')
        args = parser.parse_args()

        pyglet.options['debug_gl'] = args.debugGl
        skipToCity = args.skipToCity
        disableSound = args.disableSound
        logFile = args.logFile
        loggingLevel = args.logLevel.upper()
        overwriteLogFile = False

    logFileName = initLogger(logFile, overwrite=overwriteLogFile, level=loggingLevel)

    zippedResources = checkResources("res.zip", tempDir)
    if zippedResources:
        avbinDir = tempDir
        pyglet.resource.path = [tempDir, '']
    else:
        avbinDir = ""
        pyglet.resource.path = ['']
    pyglet.resource.reindex()

    avbinLib = pyglet.lib.load_library(os.path.join(avbinDir, 'avbin'))
    pyglet.have_avbin = True

    if zippedResources:
        import gui
        gui.tempDir = tempDir

    from gui.microWindow import MicroWindow
    app = MicroWindow(skipToCity, not disableSound)
    pyglet.app.run()

    if zippedResources:
        # cleanup temp resources
        releaseAvbin()
        shutil.rmtree(tempDir)

    deleteLogFileIfEmpty(logFileName)
