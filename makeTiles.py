'''
Created on Oct 4, 2015

creates a single tile graphics file from individual tile files


@author: chris
'''
import sys, re, math
from PIL import Image, ImageOps
from engine.tilespec import generateTilenames, parseTileSpec


class Properties(object):
    '''
    Properties class that separate lines in a files based on
    whitespace into key, value pairs. key must be at start of line.
    setting properties is not tested.
    '''
    def __init__(self):
        self._props = {}
        self._keyMap = {}
        self._origProps = {}
        self.spaceR = re.compile(r'(?<![\\])(\s)')
        
    def containsKey(self, key):
        if key in self._props:
            return True
        else:
            return False
    
    def getPropertyFlat(self, key):
        try:
            return self.unEscape(self._props[key])
        except KeyError:
            return None
    
    def getProperty(self, key):
        try:
            return self._props[key]
        except KeyError:
            return None
    
    def setProperty(self, key, value):
        # not tested!
        if type(key) is str and type(value) is str:
            self.processPair(key, value)
        else:
            raise TypeError,'both key and value should be strings!'
        
    def size(self):
        return len(self._props)
        
    def propertyNames(self):
        return self._props.keys()
    
    def __getitem__(self, name):
        return self.getProperty(name)
    
    def __setitem(self, name, value):
        self.setProperty(name, value)
        
    def __getattr(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            if hasattr(self._props,name):
                return getattr(self._props, name)
        
    def __parse(self, lines):
        ''' parse list of lines and create an 
            internal property dictionary '''
        
        lineNum = 0
        i = iter(lines)
        
        for line in i:
            lineNum += 1
            # skip null lines
            if not line: continue
            # skip lines which are comments
            if line[0] == '#': continue
            
            sepIdX = -1
            start, end = 0, len(line)
            m = self.spaceR.search(line, start, end)
            if m:
                first, last = m.span()
                sepIdX = last - 1
            
            if sepIdX != -1:
                key, value = line[:sepIdX], line[sepIdX+1:]
            else:
                key, value = line,''
            self.processPair(key, value)
        
    def processPair(self, key, value):
        oldKey = key
        oldValue = value
        
        #
        keyParts = self.spaceR.split(key)
        
        strippable = False
        lastPart = keyParts[-1]
        
        if lastPart.find('\\ ') != -1:
            keyParts[-1] = lastPart.replace('\\','')

        # If no backspace is found at the end, but empty
        # space is found, strip it
        elif lastPart and lastPart[-1] == ' ':
            strippable = True
        
        key = ''.join(keyParts)
        if strippable:
            key = key.strip()
            oldKey = oldKey.strip()
        
        oldValue = self.unEscape(oldValue)
        value = self.unEscape(value)
        
        self._props[key] = value.strip()
        
        if self._keyMap.has_key(key):
            oldKey = self._keyMap.get(key)
            self._origProps[oldKey] = oldValue.strip()
        else:
            self._origProps[oldKey] = oldValue.strip()
            self._keyMap[key] = oldKey
        
    
    def load(self, stream):
        if type(stream) is not file:
            raise TypeError,'Argument should be a file object!'
        if stream.mode != 'r':
            raise ValueError,'Stream should be opened in read-only mode'
        
        try:
            lines = stream.readlines()
            self.__parse(lines)
        except IOError, e:
            raise
        
        
    def unEscape(self, value):
        newValue = value.replace('\:', ':')
        newValue = newValue.replace('\=','=')
        return newValue
    
    
class ImageLoader(object):
    '''
    
    '''
    def __init__(self, pathPrefix=None):
        self.loadedImages = dict()
        self.pathPrefix = pathPrefix
    
    def loadImage(self, fileName):
        if fileName not in self.loadedImages:
            self.loadedImages[fileName] = self.loadImageReal(fileName)
        return self.loadedImages[fileName]
    
    def loadImageReal(self, fileName):
        try:
            path = self.pathPrefix + fileName + ".png"
            return Image.open(path)
        except IOError:
            raise IOError("ioerror:" +  path + "not found.")
            

class FrameSpec(object):
    '''
    contains specification for a image part
    '''
    def __init__(self):
        self.background = None
        self.image = None
        self.offsetX = 0
        self.offsetY = 0
        

class MakeTiles(object):
    STD_SIZE = 16
    def __init__(self, tileSize):
        self.tileSize = tileSize
        self.imageLoader = ImageLoader("graphics/")
        self.destImg = None
    
    def generateTiles(self, recipeFilename, outputName):
        '''
        
        '''
        recipe = Properties()
        recipe.load(open(recipeFilename))
    
        tileNames = generateTilenames(recipe)
        nTiles = len(tileNames)
        
        squaredSize = int(math.floor(math.sqrt(nTiles)))
        rows = squaredSize 
        columns = squaredSize + 2
        tileSize = self.tileSize
        self.destImg = Image.new("RGBA", 
                               (columns * tileSize, rows * tileSize))
        
        print "Generating Tile Sheet. size: " + str(tileSize)
        # assemble the image:
        startY = ((rows * tileSize) - tileSize)
        for tileNum in range(nTiles):
            if not(tileNum >= 0 and tileNum < nTiles):
                continue
            tileName = tileNames[tileNum]
            rawSpec = recipe.getProperty(tileName)
            assert rawSpec != None
            tileSpec = parseTileSpec(tileNum, tileName, rawSpec, recipe)
            ref = self.parseFrameSpec(tileSpec)
            if (ref == None):
                continue
            destX = tileSize * (tileNum % columns)
            destY = startY - ((tileNum / columns) * tileSize)
            self.drawTo(ref, destX, destY)
        
        self.destImg.save(outputName+str(self.tileSize)+".png")
        
    
    def parseFrameSpec(self, tileSpec):
        '''
        
        '''
        result = None
        
        for layerStr in tileSpec.getImages():
            rv = FrameSpec()
            rv.background = result
            result = rv
            
            parts = layerStr.split("@",2)
            rv.image = self.imageLoader.loadImage(parts[0])
            if len(parts) >= 2:
                offsetInfo = parts[1]
                parts = offsetInfo.split(",")
                if len(parts) >= 1:
                    rv.offsetX = int(parts[0])
                if len(parts) >= 2:
                    rv.offsetY = int(parts[1])
        return result
            
    
    def drawTo(self, ref, destX, destY):
        '''
        
        '''
        if ref.background != None:
            self.drawTo(ref.background, destX, destY)
        
        img = ref.image
        box = (ref.offsetX, ref.offsetY,
               ref.offsetX + self.STD_SIZE,
               ref.offsetY + self.STD_SIZE)
        region = img.crop(box)
        if (self.tileSize != self.STD_SIZE):
            region = region.resize((self.tileSize,self.tileSize),Image.ANTIALIAS)
        if region.mode != "RGBA":
            region = region.convert("RGBA")
        box = (destX, destY, destX+self.tileSize,destY+self.tileSize)
        self.destImg.paste(region, box, region)


if __name__ == '__main__':
    args = sys.argv
    assert len(args) > 3
    tileSize = int(args[1])
    recipeFilename = args[2]
    outputFilename = args[3]
    makeTiles = MakeTiles(tileSize)
    makeTiles.generateTiles(recipeFilename, outputFilename)