'''
Created on Oct 24, 2015

@author: chris
'''

import micropolistool
from engine.cityRect import CityRect
from engine.translatedToolEffect import TranslatedToolEffect
from tileConstants import *
from toolStroke import ToolStroke

'''
    LineTool

    Allows a tool be to placed in a single file line.
    Includes functions for road, rail, and wire.
'''


class LineTool(ToolStroke):
    def __init__(self, engine, tool, xPos, yPos):
        super(LineTool, self).__init__(engine, tool, xPos, yPos)

    '''
        overrides ToolStroke
    '''

    def applyArea(self, eff):
        while True:
            if self.applyForward(eff) == False:
                break

    def applyForward(self, eff):
        anyChange = False

        b = self.getBounds()
        for y in xrange(b.height):
            for x in xrange(b.width):
                tte = TranslatedToolEffect(eff, b.x + x, b.y + y)
                anyChange = anyChange or self.applySingle(tte)
        return anyChange

    def applyBackward(self, eff):
        anyChange = False

        b = self.getBounds()
        for y in xrange(b.height - 1, 0, -1):
            for x in xrange(b.width - 1, 0, -1):
                tte = TranslatedToolEffect(eff, b.x + x, b.y + y)
                anyChange = anyChange or self.applySingle(tte)

        return anyChange

    def getBounds(self):
        ''' constrain bounds to be rectangle with
            either width of height equal to one '''

        assert self.tool.getWidth() == 1
        assert self.tool.getHeight() == 1

        xDest = self.xDest
        xPos = self.xPos
        yDest = self.yDest
        yPos = self.yPos

        if abs(xDest - xPos) >= abs(yDest - yPos):
            # horizontal line
            r = CityRect()
            r.x = min(xPos, xDest)
            r.width = abs(xDest - xPos) + 1
            r.y = yPos
            r.height = 1
            return r
        else:
            # vertical line
            r = CityRect()
            r.x = xPos
            r.width = 1
            r.y = min(yPos, yDest)
            r.height = abs(yDest - yPos) + 1
            return r

    def applySingle(self, eff):
        if self.tool.type == micropolistool.ROADS:
            return self.applyRoadTool(eff)
        elif self.tool.type == micropolistool.RAIL:
            return self.applyRailTool(eff)
        elif self.tool.type == micropolistool.WIRE:
            return self.applyWireTool(eff)
        else:
            raise Exception("Unexpected Tool: " + self.tool.name)

    def applyWireTool(self, eff):
        if self.layWire(eff):
            self.fixZone(eff)
            return True
        else:
            return False

    def applyRailTool(self, eff):
        if self.layRail(eff):
            self.fixZone(eff)
            return True
        else:
            return False

    def applyRoadTool(self, eff):

        if self.layRoad(eff):
            self.fixZone(eff)
            return True
        else:
            return False

    def layWire(self, eff):
        WIRECOST = 5
        UNDERWATERWIRECOST = 25

        cost = WIRECOST

        tile = eff.getTile(0, 0)
        tile = neutralizeRoad(tile)

        if (tile == RIVER
            or tile == REDGE
            or tile == CHANNEL):
            cost = UNDERWATERWIRECOST

            hit = False
            eastT = neutralizeRoad(eff.getTile(1, 0))
            if (isConductive(eastT) and
                    eastT != HROADPOWER and
                    eastT != RAILHPOWERV and
                    eastT != HPOWER):
                eff.setTile(0, 0, VPOWER)
                hit = True
            if not hit:
                westT = neutralizeRoad(eff.getTile(-1, 0))
                if (isConductive(westT) and
                        westT != HROADPOWER and
                        westT != RAILHPOWERV and
                        westT != HPOWER):
                    eff.setTile(0, 0, VPOWER)
                    hit = True
            if not hit:
                southT = neutralizeRoad(eff.getTile(0, 1))
                if (isConductive(southT) and
                        southT != VROADPOWER and
                        southT != RAILVPOWERH and
                        southT != VPOWER):
                    eff.setTile(0, 0, HPOWER)
                    hit = True
            if not hit:
                northTile = neutralizeRoad(eff.getTile(0, -1))
                if (isConductive(northTile) and
                        northTile != VROADPOWER and
                        northTile != RAILVPOWERH and
                        northTile != VPOWER):
                    eff.setTile(0, 0, HPOWER)
                    hit = True

            if not hit:
                return False

        elif tile == ROADS:
            eff.setTile(0, 0, HROADPOWER)

        elif tile == ROADS2:
            eff.setTile(0, 0, VROADPOWER)

        elif tile == LHRAIL:
            eff.setTile(0, 0, RAILHPOWERV)

        elif tile == LVRAIL:
            eff.setTile(0, 0, RAILVPOWERH)

        else:
            if tile != DIRT:
                if canAutoBulldozeRRW(tile) and self.engine.autoBulldoze:
                    cost += 1
                else:
                    return False

            eff.setTile(0, 0, LHPOWER)

        eff.spend(cost)
        return True

    def layRail(self, eff):
        RAILCOST = 20
        TUNNELCOST = 100

        cost = RAILCOST

        tile = eff.getTile(0, 0)
        tile = neutralizeRoad(tile)

        if (tile == RIVER
            or tile == REDGE
            or tile == CHANNEL):
            cost = TUNNELCOST

            hit = False
            eastT = neutralizeRoad(eff.getTile(1, 0))
            if (eastT == RAILHPOWERV or eastT == HRAIL or
                    (LHRAIL <= eastT <= HRAILROAD)):
                eff.setTile(0, 0, HRAIL)
                hit = True
            if not hit:
                westT = neutralizeRoad(eff.getTile(-1, 0))
                if (westT == RAILHPOWERV or westT == HRAIL or
                        (VRAIL < westT < VRAILROAD)):
                    eff.setTile(0, 0, HRAIL)
                    hit = True
            if not hit:
                southT = neutralizeRoad(eff.getTile(0, 1))
                if (southT == RAILVPOWERH or southT == VRAILROAD or
                        (HRAIL < southT < HRAILROAD)):
                    eff.setTile(0, 0, VRAIL)
                    hit = True
            if not hit:
                northTile = neutralizeRoad(eff.getTile(0, -1))
                if (northTile == RAILVPOWERH or northTile == VRAILROAD or
                        (HRAIL < northTile < HRAILROAD)):
                    eff.setTile(0, 0, VRAIL)
                    hit = True

            if not hit:
                return False

        elif tile == LHPOWER:
            eff.setTile(0, 0, RAILVPOWERH)

        elif tile == LVPOWER:
            eff.setTile(0, 0, RAILHPOWERV)

        elif tile == ROADS:
            eff.setTile(0, 0, VRAILROAD)

        elif tile == ROADS2:
            eff.setTile(0, 0, HRAILROAD)

        else:
            if tile != DIRT:
                if canAutoBulldozeRRW(tile) and self.engine.autoBulldoze:
                    cost += 1
                else:
                    return False

            eff.setTile(0, 0, LHRAIL)

        eff.spend(cost)
        return True

    def layRoad(self, eff):
        ROADCOST = 10
        BRIDGECOST = 50

        cost = ROADCOST

        tile = eff.getTile(0, 0)
        if tile == RIVER or \
                        tile == REDGE or \
                        tile == CHANNEL:
            cost = BRIDGECOST

            hit = False
            eTile = neutralizeRoad(eff.getTile(1, 0))
            if (eTile == VRAILROAD or eTile == HBRIDGE or
                    (ROADS <= eTile <= HROADPOWER)):
                eff.setTile(0, 0, HBRIDGE)
                hit = True
            if not hit:
                wTile = neutralizeRoad(eff.getTile(-1, 0))
                if (wTile == VRAILROAD or wTile == HBRIDGE or
                        (ROADS <= wTile <= INTERSECTION)):
                    eff.setTile(0, 0, HBRIDGE)
                    hit = True
            if not hit:
                sTile = neutralizeRoad(eff.getTile(0, 1))
                if (sTile == HRAILROAD or sTile == VROADPOWER or
                        (VBRIDGE <= sTile <= INTERSECTION)):
                    eff.setTile(0, 0, VBRIDGE)
                    hit = True
            if not hit:
                nTile = neutralizeRoad(eff.getTile(0, -1))
                if (nTile == HRAILROAD or nTile == VROADPOWER or
                        (VBRIDGE <= nTile <= INTERSECTION)):
                    eff.setTile(0, 0, VBRIDGE)
                    hit = True

            if not hit:
                return False

        elif tile == LHPOWER:
            eff.setTile(0, 0, VROADPOWER)
        elif tile == LVPOWER:
            eff.setTile(0, 0, HROADPOWER)
        elif tile == LHRAIL:
            eff.setTile(0, 0, HRAILROAD)
        elif tile == LVRAIL:
            eff.setTile(0, 0, VRAILROAD)
        else:
            if tile != DIRT:
                if canAutoBulldozeRRW(tile) and self.engine.autoBulldoze:
                    cost += 1
                else:
                    return False

            eff.setTile(0, 0, ROADS)

        eff.spend(cost)
        return True
