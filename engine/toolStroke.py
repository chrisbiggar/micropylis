'''
Created on Oct 22, 2015

@author: chris
'''
import micropolistool
from engine.cityLocation import CityLocation
from engine.cityRect import CityRect
from engine.toolResult import ToolResult
from engine.translatedToolEffect import TranslatedToolEffect
from tileConstants import *
from toolEffect import ToolEffect
import tiles

'''
    ToolStroke

    Base class for applying tile changes of a tool to a ToolEffect obj.
    Contains functions for "fixing" surrounding tiles.
'''


class ToolStroke(object):
    def __init__(self, engine, tool, xPos, yPos):
        self.engine = engine
        self.tool = tool
        self.xPos = xPos
        self.yPos = yPos
        self.xDest = xPos
        self.yDest = yPos
        self.inPreview = False

    def getPreview(self):
        eff = ToolEffect(self.engine)
        self.inPreview = True
        try:
            self.applyArea(eff)
        finally:
            self.inPreview = False
        return eff.preview

    def apply(self):
        eff = ToolEffect(self.engine)
        self.applyArea(eff)
        return eff.apply()

    def applyArea(self, eff):
        r = self.getBounds()

        for x in xrange(0, r.width, self.tool.getWidth()):
            for y in xrange(0, r.height, self.tool.getHeight()):
                self.apply1(TranslatedToolEffect(eff, r.x + x, r.y + y))

    def apply1(self, eff):
        if self.tool.type == micropolistool.PARK:
            return self.applyParkTool(eff)
        elif self.tool.type == micropolistool.RESIDENTIAL:
            return self.applyZone(eff, RESCLR)
        elif self.tool.type == micropolistool.COMMERCIAL:
            return self.applyZone(eff, COMCLR)
        elif self.tool.type == micropolistool.INDUSTRIAL:
            return self.applyZone(eff, INDCLR)
        else:
            raise Exception("unexpected tool: " + self.tool.name)

    def dragTo(self, xDest, yDest):
        self.xDest = xDest
        self.yDest = yDest

    def getBounds(self):
        xPos = self.xPos
        xDest = self.xDest
        yPos = self.yPos
        yDest = self.yDest
        width = self.tool.getWidth()
        height = self.tool.getHeight()
        r = CityRect()

        r.x = xPos
        if width >= 3:
            r.x -= 1
        if xDest >= xPos:
            r.width = ((xDest - xPos) / width + 1) * width
        else:
            r.width = ((xPos - xDest) / width + 1) * height
            r.x += width - r.width

        r.y = yPos
        if height >= 3:
            r.y -= 1
        if yDest > yPos:
            r.height = ((yDest - yPos) / height + 1) * height
        else:
            # tool dragged upwards
            r.height = (((yPos - yDest) / height) + 1) * height
            r.y -= r.height - height

        return r

    def getLocation(self):
        return CityLocation(self.xPos, self.yPos)

    '''
        Given a base(center) tile number, will draw
        that specific zone in place of given eff.
    '''
    def applyZone(self, eff, base):
        assert isZoneCenter(base)

        bi = tiles.get(base).getBuildingInfo()
        if bi is None:
            # TODO throw error
            print("error. cannot applyzone to #" + str(base))
            return False

        cost = self.tool.getToolCost()
        for rowNum in xrange(bi.height):
            for columnNum in xrange(bi.width):
                tileValue = eff.getTile(columnNum, rowNum)
                tileValue = tileValue & LOMASK

                if tileValue != DIRT:
                    if canAutoBulldozeZ(tileValue) and self.engine.autoBulldoze:
                        cost += 1
                    else:
                        # TODO if tile water set tool result to NONE

                        eff.toolResult(ToolResult.UH_OH)
                        return False

        eff.spend(cost)

        i = 0
        # TODO optimize this by storing full zones and just copying that here?
        for rowNum in xrange(bi.height):
            for columnNum in xrange(bi.width):
                eff.setTile(columnNum, rowNum, bi.members[i])
                i += 1

        self.fixBorder(eff, bi.width, bi.height)
        return True

    # def fixBorder

    def fixBorder(self, eff, width, height):
        for x in xrange(width):
            self.fixZone(TranslatedToolEffect(eff, x, 0))
            self.fixZone(TranslatedToolEffect(eff, x, height - 1))
        for y in xrange(height - 1):
            self.fixZone(TranslatedToolEffect(eff, 0, y))
            self.fixZone(TranslatedToolEffect(eff, width - 1, y))

    def applyParkTool(self, eff):
        print("park")

    def fixZoneSpecific(self, xPos, yPos):
        eff = ToolEffect(self.engine, xPos, yPos)
        self.fixZone(eff)
        eff.apply()

    def fixZone(self, eff):
        self.fixSingle(eff)

        # "fix" the cells bordering this one
        self.fixSingle(TranslatedToolEffect(eff, 0, -1))
        self.fixSingle(TranslatedToolEffect(eff, -1, 0))
        self.fixSingle(TranslatedToolEffect(eff, 1, 0))
        self.fixSingle(TranslatedToolEffect(eff, 0, 1))

    def fixSingle(self, eff):
        tile = eff.getTile(0, 0)
        if isRoadDynamic(tile):
            adjTile = 0

            if roadConnectsSouth(eff.getTile(0, -1)):
                adjTile |= 1

            if roadConnectsWest(eff.getTile(1, 0)):
                adjTile |= 2

            if roadConnectsNorth(eff.getTile(0, 1)):
                adjTile |= 4

            if roadConnectsEast(eff.getTile(-1, 0)):
                adjTile |= 8

            eff.setTile(0, 0, ROADTABLE[adjTile])

        elif isRailDynamic(tile):
            adjTile = 0

            if railConnectsSouth(eff.getTile(0, -1)):
                adjTile |= 1

            if railConnectsWest(eff.getTile(1, 0)):
                adjTile |= 2

            if railConnectsNorth(eff.getTile(0, 1)):
                adjTile |= 4

            if railConnectsEast(eff.getTile(-1, 0)):
                adjTile |= 8

            eff.setTile(0, 0, RAILTABLE[adjTile])

        elif isWireDynamic(tile):
            adjTile = 0

            if wireConnectsSouth(eff.getTile(0, -1)):
                adjTile |= 1

            if wireConnectsWest(eff.getTile(1, 0)):
                adjTile |= 2

            if wireConnectsNorth(eff.getTile(0, 1)):
                adjTile |= 4

            if wireConnectsEast(eff.getTile(-1, 0)):
                adjTile |= 8

            eff.setTile(0, 0, WIRETABLE[adjTile])
