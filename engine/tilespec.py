import re
from cityDimension import CityDimension


'''
    creates a tileName->tilenum dict.

'''
def generateTilenames(recipe):
    nTiles = recipe.size()
    tileNames = [0] * (nTiles - 1)
    nTiles = 0

    while (recipe.containsKey(str(nTiles))):
        tileNames[nTiles] = str(nTiles)
        nTiles += 1
    naturalNumTiles = nTiles

    for name in recipe.propertyNames():
        # test for integer:
        if re.match("^\\d+$", name):
            num = int(name)
            if (num >= 0 and num < naturalNumTiles):
                assert tileNames[num] == name
                continue
            assert nTiles < len(tileNames)
            tileNames[nTiles] = name
            nTiles += 1
    assert nTiles == len(tileNames)
    return tileNames

'''
    convienience function for loading tile specs
'''
def parseTileSpec(tileNum, tileName, inStr, tilesRc):

    ts = TileSpec(tileNum, tileName)
    ts.load(inStr, tilesRc)
    return ts


class BuildingInfo(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.members = []


'''
    Scanner

    Decodes a single tilespec
'''


class Scanner(object):
    def __init__(self, aStr):
        self.str = aStr
        self.offset = 0

    def skipWhitespace(self):
        while (self.offset < len(self.str) and
                   self.str[self.offset].isspace()):
            self.offset += 1

    def peekChar(self):
        self.skipWhitespace()
        if (self.offset < len(self.str)):
            return self.str[self.offset]
        else:
            return -1

    def eatChar(self, ch):
        self.skipWhitespace()
        assert self.str[self.offset] == ch
        self.offset += 1

    def readAttributeKey(self):
        self.skipWhitespace()
        start = self.offset
        while (self.offset < len(self.str) and \
                       (self.str[self.offset] == '-' or \
                                self.str[self.offset].isalnum())):
            self.offset += 1
        if (self.offset != start):
            return self.str[start:self.offset]
        else:
            return None

    def readAttributeValue(self):
        return self.readString()

    def readImageSpec(self):
        return self.readString()

    def readString(self):
        self.skipWhitespace()
        endQuote = 0
        if (self.peekChar() == '"'):
            self.offset += 1
            endQuote = '"'
        start = self.offset
        while (self.offset < len(self.str)):
            c = self.str[self.offset]
            if (c == endQuote):
                end = self.offset
                self.offset += 1
                return self.str[start:end]
            elif (endQuote == 0 and
                      (c.isspace() or
                               c == ')' or
                               c == '|')):
                end = self.offset
                return self.str[start:end]
            self.offset += 1
        return self.str[start:len(self.str)]

    def hasMore(self):
        return (self.peekChar() != -1)


'''
    TileSpec

    Contains the attributes for a single tile.
'''


class TileSpec(object):
    def __init__(self, tileNum, tileName):
        self.tileNum = tileNum
        self.tileName = tileName
        self._attributes = dict()
        self._images = list()
        self.buildingInfo = None
        self.owner = None
        self.animNext = None
        self.onPower = None
        self.onShutdown = None

    def load(self, inStr, tilesRc):
        '''
        
        '''
        scanner = Scanner(inStr)

        while scanner.hasMore():
            if scanner.peekChar() == '(':
                scanner.eatChar('(')
                k = scanner.readAttributeKey()
                v = True
                if (scanner.peekChar() == '='):
                    scanner.eatChar('=')
                    v = scanner.readAttributeValue()
                scanner.eatChar(')')

                if k not in self._attributes:
                    self._attributes[k] = v
                    # loads referenced tile
                    sup = tilesRc.getPropertyFlat(k)
                    if sup != None:
                        self.load(sup, tilesRc)
                else:
                    self._attributes[k] = v


            elif (scanner.peekChar() == '|' or
                          scanner.peekChar() == ','):
                scanner.eatChar(scanner.peekChar())

            else:
                v = scanner.readImageSpec()
                self._images.append(v)

        self.canBulldoze = self.getBooleanAttribute("bulldozable")
        self.canBurn = not self.getBooleanAttribute("noburn")
        self.canConduct = self.getBooleanAttribute("conducts")
        self.overWater = self.getBooleanAttribute("overwater")
        self.zone = self.getBooleanAttribute("zone")

    def resolveBuildingInfo(self):
        tmp = self.getAttribute("building")
        if tmp is None:
            return

        bi = BuildingInfo()

        p2 = tmp.split("x")
        bi.width = int(p2[0])
        bi.height = int(p2[1])

        bi.members = [0] * bi.width * bi.height
        startTile = self.tileNum
        if bi.width >= 3:
            startTile -= 1
        if bi.height >= 3:
            startTile -= bi.width

        for row in xrange(bi.height):
            for col in xrange(bi.width):
                bi.members[row * bi.width + col] = startTile
                startTile += 1

        self.buildingInfo = bi

    def getBuildingSize(self):
        if self.buildingInfo is not None:
            return CityDimension(self.buildingInfo.width,
                                 self.buildingInfo.height)
        else:
            return None

    def resolveReferences(self, tileMap):
        tmp = self.getAttribute("becomes")
        if tmp is not None:
            self.animNext = tileMap.get(tmp)
        tmp = self.getAttribute("onpower")
        if tmp is not None:
            self.onPower = tileMap.get(tmp)
        tmp = self.getAttribute("onshutdown")
        if tmp is not None:
            self.onShutdown = tileMap.get(tmp)
        tmp = self.getAttribute("building-part")
        if tmp is not None:
            self.handleBuildingPart(tmp, tileMap)

        self.resolveBuildingInfo()

    def handleBuildingPart(self, text, tileMap):
        parts = text.split(",")
        if len(parts) != 3:
            print "invalid building-part spec"
            return
        self.owner = tileMap.get(parts[0])
        self.ownerOffsetX = int(parts[1])
        self.ownerOffsetY = int(parts[2])

        assert self.owner is not None
        assert self.ownerOffsetX != 0 or self.ownerOffsetY != 0

    def isNumberedTile(self):
        # regex to match name
        pass

    def getBuildingInfo(self):
        return self.buildingInfo

    def getImages(self):
        return self._images

    def getPollutionValue(self):
        v = self.getAttribute("pollution")
        if v is not None:
            return int(v)
        elif self.owner is not None:
            return self.owner.getPollutionValue()
        else:
            return 0

    def getPopulation(self):
        v = self.getAttribute("population")
        if v is not None:
            return int(v)
        else:
            return 0

    def getBooleanAttribute(self, key):
        if key in self._attributes:
            return True
        else:
            return False

    def getAttribute(self, key):
        return self._attributes.get(key)
