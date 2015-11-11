'''
Created on Sep 24, 2015

 * Contains symbolic names of certain tile values,
 * and helper functions to test tile attributes.

@author: chris
'''
import engine.tiles as tiles
from pyglet.image import TileableTexture
from engine.tiles import Tiles


CLEAR = -1
DIRT = 0
RIVER = 2
REDGE = 3
CHANNEL = 4
RIVEDGE = 5
FIRSTRIVEDGE = 5
LASTRIVEDGE = 20
TREEBASE = 21
WOODS_LOW = TREEBASE
WOODS = 37
WOODS_HIGH = 39
WOODS2 = 40
WOODS5 = 43
RUBBLE = 44
LASTRUBBLE = 47
FLOOD = 48
LASTFLOOD = 51
RADTILE = 52
FIRE = 56
ROADBASE = 64
HBRIDGE = 64
VBRIDGE = 65
ROADS = 66
ROADS2 = 67
ROADS3 = 68
ROADS4 = 69
ROADS5 = 70
ROADS6 = 71
ROADS7 = 72
ROADS8 = 73
ROADS9 = 74
ROADS10 = 75
INTERSECTION = 76
HROADPOWER = 77
VROADPOWER = 78
BRWH = 79       #horz bridge, open
LTRFBASE = 80
BRWV = 95       #vert bridge, open
HTRFBASE = 144
LASTROAD = 206
POWERBASE = 208
HPOWER = 208    #underwater power-line
VPOWER = 209
LHPOWER = 210
LVPOWER = 211
LVPOWER2 = 212
LVPOWER3 = 213
LVPOWER4 = 214
LVPOWER5 = 215
LVPOWER6 = 216
LVPOWER7 = 217
LVPOWER8 = 218
LVPOWER9 = 219
LVPOWER10 = 220
RAILHPOWERV = 221
RAILVPOWERH = 222
LASTPOWER = 222
RAILBASE = 224
HRAIL = 224     #underwater rail (horz)
VRAIL = 225     #underwater rail (vert)
LHRAIL = 226
LVRAIL = 227
LVRAIL2 = 228
LVRAIL3 = 229
LVRAIL4 = 230
LVRAIL5 = 231
LVRAIL6 = 232
LVRAIL7 = 233
LVRAIL8 = 234
LVRAIL9 = 235
LVRAIL10 = 236
HRAILROAD = 237
VRAILROAD = 238
LASTRAIL = 238

LOMASK = 1023 # mask for low ten bits

RESBASE = 244
RESCLR = 244

COMCLR = 427


INDCLR = 616

TINYEXP = 860
LASTTINYEXP = 867




ROADTABLE = [
    ROADS, ROADS2, ROADS, ROADS3,
    ROADS2, ROADS2, ROADS4, ROADS8,
    ROADS, ROADS6, ROADS, ROADS7,
    ROADS5, ROADS10, ROADS9, INTERSECTION]

RAILTABLE = [
    LHRAIL, LVRAIL, LHRAIL, LVRAIL2,
    LVRAIL, LVRAIL, LVRAIL3, LVRAIL7,
    LHRAIL, LVRAIL5, LHRAIL, LVRAIL6,
    LVRAIL4, LVRAIL9, LVRAIL8, LVRAIL10]

WIRETABLE = [
    LHPOWER, LVPOWER, LHPOWER, LVPOWER2,
    LVPOWER, LVPOWER, LVPOWER3, LVPOWER7,
    LHPOWER, LVPOWER5, LHPOWER, LVPOWER6,
    LVPOWER4, LVPOWER9, LVPOWER8, LVPOWER10]


def canAutoBulldozeRRW(tile):
    ''' checks whether tile can be bulldozed for
        placement of a road, rail, or wire. '''
    return ((tile >= FIRSTRIVEDGE and tile <= LASTRUBBLE)
        or
        (tile >= TINYEXP and tile <= LASTTINYEXP))

def canAutoBulldozeZ(tile):
    ''' checks whether tile can be bulldozed for
        placement of a zone '''
    
    if ((tile >= FIRSTRIVEDGE and tile <= LASTRUBBLE) 
            or (tile >= POWERBASE + 2 and tile <= POWERBASE + 12)
            or (tile >= TINYEXP and tile <= LASTTINYEXP)):
        return True
    else:
        return False

def getTileBehaviour(tile):
    ts = Tiles().get(tile)
    return ts.getAttribute("behaviour")


def isRoadDynamic(tile):
    ''' checks if tile is road than can change to
        connect to neighboring roads'''
    tmp = neutralizeRoad(tile)
    return tmp >= ROADS and tmp <= INTERSECTION

def roadConnectsEast(tile):
    tile = neutralizeRoad(tile)
    return tile == VRAILROAD or\
        tile >= ROADBASE and tile <= VROADPOWER\
        and\
        tile != VROADPOWER and\
        tile != HRAILROAD and\
        tile != VBRIDGE

def roadConnectsNorth(tile):
    tile = neutralizeRoad(tile)
    return (tile == HRAILROAD or\
            (tile >= ROADBASE and tile <= VROADPOWER))\
            and\
            tile != HROADPOWER and\
            tile != VRAILROAD and\
            tile != ROADBASE

def roadConnectsSouth(tile):
    tile = neutralizeRoad(tile)
    return (tile == HRAILROAD) or\
        (tile >= ROADBASE and tile <= VROADPOWER)\
        and\
        tile != HROADPOWER and\
        tile != VRAILROAD and\
        tile != ROADBASE

def roadConnectsWest(tile):
    tile = neutralizeRoad(tile)
    return (tile == VRAILROAD) or\
        (tile >= ROADBASE and tile <= VROADPOWER)\
        and\
        tile != VROADPOWER and\
        tile != HRAILROAD and\
        tile != VBRIDGE
        
def isRail(tile):
    assert tile & LOMASK == tile
    
    return (tile >= RAILBASE and tile < RESBASE)\
        or tile == RAILHPOWERV\
        or tile == RAILVPOWERH
        
def isRailDynamic(tile):
    assert tile & LOMASK == tile
    
    return tile >= LHRAIL and tile <= LVRAIL10

def railConnectsEast(tile):
    tile = neutralizeRoad(tile)
    return (tile >= RAILHPOWERV and tile <= VRAILROAD and\
        tile != RAILVPOWERH and\
        tile != VRAILROAD and\
        tile != VRAIL)

def railConnectsNorth(tile):
    tile = neutralizeRoad(tile)
    return (tile >= RAILHPOWERV and tile <= VRAILROAD and
        tile != RAILHPOWERV and
        tile != HRAILROAD and
        tile != HRAIL)

def railConnectsSouth(tile):
    tile = neutralizeRoad(tile)
    
    return (tile >= RAILHPOWERV and tile <= VRAILROAD and
        tile != RAILHPOWERV and
        tile != HRAILROAD and
        tile != HRAIL)

def railConnectsWest(tile):
    tile = neutralizeRoad(tile)
    return (tile >= RAILHPOWERV and tile <= VRAILROAD and
        tile != RAILVPOWERH and
        tile != VRAILROAD and
        tile != VRAIL)
    

def isConductive(tile):
    assert tile & LOMASK == tile
    spec = Tiles().get(tile)
    return spec is not None and spec.canConduct
    
def isWireDynamic(tile):
    assert tile & LOMASK == tile
    
    return tile >= LHPOWER and tile <= LVPOWER10

def wireConnectsEast(tile):
    ntile = neutralizeRoad(tile)
    return (isConductive(tile) and
        ntile != HPOWER and
        ntile != HROADPOWER and
        ntile != RAILHPOWERV)

def wireConnectsNorth(tile):
    ntile = neutralizeRoad(tile)
    return (isConductive(tile) and
        ntile != VPOWER and
        ntile != VROADPOWER and
        ntile != RAILVPOWERH)

def wireConnectsSouth(tile):
    ntile = neutralizeRoad(tile)
    return (isConductive(tile) and
        ntile != VPOWER and
        ntile != VROADPOWER and
        ntile != RAILVPOWERH)

def wireConnectsWest(tile):
    ntile = neutralizeRoad(tile)
    return (isConductive(tile) and
        ntile != HPOWER and
        ntile != HROADPOWER and
        ntile != RAILHPOWERV)


def neutralizeRoad(tile):
    assert (tile & LOMASK) == tile
    
    if tile >= ROADBASE and tile <= LASTROAD:
        tile = ((tile - ROADBASE) & 0xf) + ROADBASE
    return tile


def isZoneCenter(tile):
    assert tile & LOMASK == tile
    
    spec = Tiles().get(tile)
    return spec is not None and spec.zone












