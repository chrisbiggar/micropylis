from tilespec import parseTileSpec, generateTilenames
from util.properties import Properties

'''
    Tiles

    Provides access to tilespec objects for all tiles.
    Functions as singleton, only loading data at first creation.
    Uses Borg pattern for singleton behaviour.
'''

class LocalScope(object):
    tiles = None
    tilesByName = None
loc = LocalScope()

def getByName(name):
    return loc.tilesByName[name]


def get(num):
    try:
        return loc.tiles[num]
    except KeyError:
        return None


def readTilesSpec(tilesSpecFile):
    tilesRc = Properties()
    tilesRc.load(open(tilesSpecFile))
    tileNames = generateTilenames(tilesRc)

    tiles = [0 for i in xrange(len(tileNames))]
    tilesByName = dict()

    for i in xrange(len(tileNames)):
        tileName = tileNames[i]
        rawSpec = tilesRc.getProperty(tileName)
        if rawSpec is None:
            break

        ts = parseTileSpec(i, tileName, rawSpec, tilesRc)
        tilesByName[tileName] = ts
        tiles[i] = ts

    for i in xrange(len(tiles)):
        tiles[i].resolveReferences(tilesByName)
        bi = tiles[i].getBuildingInfo()
        if bi is not None:
            for j in xrange(len(bi.members)):
                tId = bi.members[j]
                offX = (-1 if (bi.width >= 3) else 0) + j % bi.width
                offY = (-1 if bi.height >= 3 else 0) + j / bi.width

                if (tiles[tId].owner is None
                    and (offX != 0 or offY != 0)):
                    tiles[tId].owner = tiles[i]
                    tiles[tId].ownerOffsetX = offX
                    tiles[tId].ownerOffsetY = offY
    loc.tiles = tiles
    loc.tilesByName = tilesByName