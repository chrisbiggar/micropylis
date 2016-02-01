import micropolistool
from engine import tileConstants
from toolStroke import ToolStroke

'''
    BuildingTool

    Allows a building to be placed.

    :arg tool: micropolistool corresponding to building to place
'''


class BuildingTool(ToolStroke):
    def __init__(self, engine, tool, xPos, yPos):
        super(BuildingTool, self).__init__(engine, tool, xPos, yPos)

    def dragTo(self, xDest, yDest):
        self.xPos = xDest
        self.yPos = yDest
        self.xDest = xDest
        self.yDest = yDest

    def apply1(self, eff):
        if self.tool.type == micropolistool.FIRE:
            return self.applyZone(eff, tileConstants.FIRESTATION)
        elif self.tool.type == micropolistool.POLICE:
            return self.applyZone(eff, tileConstants.POLICESTATION)
        elif self.tool.type == micropolistool.POWERPLANT:
            return self.applyZone(eff, tileConstants.POWERPLANT)
        elif self.tool.type == micropolistool.STADIUM:
            return self.applyZone(eff, tileConstants.STADIUM)
        elif self.tool.type == micropolistool.SEAPORT:
            return self.applyZone(eff, tileConstants.PORT)
        elif self.tool.type == micropolistool.NUCLEAR:
            return self.applyZone(eff, tileConstants.NUCLEAR)
        elif self.tool.type == micropolistool.AIRPORT:
            return self.applyZone(eff, tileConstants.AIRPORT)
        else:
            print "Unexpected Tool #: " + str(self.tool.type)
