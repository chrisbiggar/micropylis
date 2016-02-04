'''
Created on Sep 24, 2015

 * Contains symbolic names of certain tile values,
 * and helper functions to test tile attributes.

@author: chris
'''
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
BRWH = 79  # horz bridge, open
LTRFBASE = 80
BRWV = 95  # vert bridge, open
HTRFBASE = 144
LASTROAD = 206
POWERBASE = 208
HPOWER = 208  # underwater power-line
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
HRAIL = 224  # underwater rail (horz)
VRAIL = 225  # underwater rail (vert)
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
RESBASE = 244
RESCLR = 244
HOUSE = 249
LHTHR = 249  # 12 house tiles
HHTHR = 260
RZB = 265  # residential zone base
HOSPITAL = 409
CHURCH = 418
COMBASE = 423
COMCLR = 427
CZB = 436  # commercial zone base
INDBASE = 612
INDCLR = 616
IZB = 625
PORTBASE = 693
PORT = 698
AIRPORT = 716
POWERPLANT = 750
FIRESTATION = 765
POLICESTATION = 774
STADIUM = 784
FULLSTADIUM = 800
NUCLEAR = 816

LIGHTNINGBOLT = 827

TINYEXP = 860
LASTTINYEXP = 867

LASTTILE = 956

PWRBIT = 32768  # bit 15 indicates powered state

ALLBITS = 64512
LOMASK = 1023  # mask for low ten bits

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
    return (FIRSTRIVEDGE <= tile <= LASTRUBBLE or
            TINYEXP <= tile <= LASTTINYEXP)


'''
checks whether tile can be bulldozed for
placement of a zone
'''
def canAutoBulldozeZ(tile):


    if ((FIRSTRIVEDGE <= tile <= LASTRUBBLE) or
            (POWERBASE + 2 <= tile <= POWERBASE + 12) or
            (TINYEXP <= tile <= LASTTINYEXP)):
        return True
    else:
        return False


def getTileBehaviour(tile):
    ts = Tiles().get(tile)
    b = ts.getAttribute("behavior")
    return b


def getZoneSizeFor(tile):
    assert isZoneCenter(tile)
    assert tile & LOMASK == tile

    spec = Tiles().get(tile)
    if spec is None:
        return None
    return spec.getBuildingSize()


def isRoadDynamic(tile):
    ''' checks if tile is road than can change to
        connect to neighboring roads'''
    tmp = neutralizeRoad(tile)
    return ROADS <= tmp <= INTERSECTION


def roadConnectsEast(tile):
    tile = neutralizeRoad(tile)
    return (tile == VRAILROAD or
               tile >= ROADBASE and tile <= VROADPOWER
               and
               tile != VROADPOWER and
               tile != HRAILROAD and
               tile != VBRIDGE)


def roadConnectsNorth(tile):
    tile = neutralizeRoad(tile)
    return ((tile == HRAILROAD or
            (tile >= ROADBASE and tile <= VROADPOWER))
           and
           tile != HROADPOWER and
           tile != VRAILROAD and
           tile != ROADBASE)


def roadConnectsSouth(tile):
    tile = neutralizeRoad(tile)
    return ((tile == HRAILROAD) or
            (ROADBASE <= tile <= VROADPOWER)
            and
            tile != HROADPOWER and
            tile != VRAILROAD and
            tile != ROADBASE)


def roadConnectsWest(tile):
    tile = neutralizeRoad(tile)
    return ((tile == VRAILROAD) or
            (ROADBASE <= tile <= VROADPOWER)
            and
            tile != VROADPOWER and
            tile != HRAILROAD and
            tile != VBRIDGE)


def isRail(tile):
    assert tile & LOMASK == tile

    return ((RAILBASE <= tile < RESBASE)
            or tile == RAILHPOWERV
            or tile == RAILVPOWERH)


def isRailDynamic(tile):
    assert tile & LOMASK == tile

    return LHRAIL <= tile <= LVRAIL10


def railConnectsEast(tile):
    tile = neutralizeRoad(tile)
    return (RAILHPOWERV <= tile <= VRAILROAD and
            tile != RAILVPOWERH and
            tile != VRAILROAD and
            tile != VRAIL)


def railConnectsNorth(tile):
    tile = neutralizeRoad(tile)
    return (RAILHPOWERV <= tile <= VRAILROAD and
            tile != RAILHPOWERV and
            tile != HRAILROAD and
            tile != HRAIL)


def railConnectsSouth(tile):
    tile = neutralizeRoad(tile)

    return (RAILHPOWERV <= tile <= VRAILROAD and
            tile != RAILHPOWERV and
            tile != HRAILROAD and
            tile != HRAIL)


def railConnectsWest(tile):
    tile = neutralizeRoad(tile)
    return (RAILHPOWERV <= tile <= VRAILROAD and
            tile != RAILVPOWERH and
            tile != VRAILROAD and
            tile != VRAIL)


def isCombustible(tile):
    assert (tile & LOMASK) == tile
    spec = Tiles().get(tile)
    return spec is not None and spec.canBurn


def isConductive(tile):
    assert tile & LOMASK == tile
    spec = Tiles().get(tile)
    return spec is not None and spec.canConduct


def isWireDynamic(tile):
    assert tile & LOMASK == tile

    return LHPOWER <= tile <= LVPOWER10


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


def isZoneCenter(tile):
    assert (tile & LOMASK) == tile
    spec = Tiles().get(tile)
    return spec is not None and spec.zone


def isAnimated(tile):
    assert tile & LOMASK == tile

    spec = Tiles().get(tile)
    return spec is not None and spec.animNext is not None


def isIndestructible(tile):
    assert tile & LOMASK == tile
    return FLOOD <= tile < ROADBASE


def isRubble(tile):
    assert tile & LOMASK == tile
    return RUBBLE <= tile <= LASTRUBBLE

def isOverWater(tile):
    assert tile & LOMASK == tile

    spec = Tiles().get(tile)
    return spec != None and spec.overWater


'''

'''
def neutralizeRoad(tile):
    assert (tile & LOMASK) == tile

    if tile >= ROADBASE and tile <= LASTROAD:
        tile = ((tile - ROADBASE) & 0xf) + ROADBASE
    return tile

def residentialZonePop(tile):
    assert tile & LOMASK == tile

    ts = Tiles().get(tile)
    return ts.getPopulation()