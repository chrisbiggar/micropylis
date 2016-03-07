'''
Created on Oct 22, 2015

@author: chris
'''
from engine.tileConstants import CLEAR
from .toolPreview import ToolPreview
from .toolResult import ToolResult

'''
    ToolEffect

    Applies the tile modifications made by a ToolStroke obj to a ToolPreview obj.
    Calling apply will attempt to make these modifications permanent to engine.
'''


class ToolEffect(object):
    def __init__(self, engine, xPos=0, yPos=0):
        self.engine = engine
        self.preview = ToolPreview()
        self.originX = xPos
        self.originY = yPos

    def getTile(self, dx, dy):
        c = self.preview.getTile(dx, dy)

        if c != CLEAR:
            return c

        if self.engine.testBounds(self.originX + dx, self.originY + dy):
            return self.engine.getTile(self.originX + dx,
                                       self.originY + dy)
        else:
            # tiles outside city boundary assumed dirt (tile 0)
            return 0

    def setTile(self, dx, dy, tileValue):
        self.preview.setTile(dx, dy, tileValue)

    def spend(self, amount):
        self.preview.spend(amount)

    def toolResult(self, tr):
        self.preview.setToolResult(tr)

    def makeSound(self, dx, dy, sound):
        self.preview.makeSound(dx, dy, sound)

    def apply(self):
        ''' actually apply the effect to the map
            
        '''
        if ((self.originX - self.preview.offsetX < 0 or
                self.originX - self.preview.offsetX + self.preview.getWidth() > self.engine.getWidth()) or
                self.originY - self.preview.offsetY < 0 or
                self.originY - self.preview.offsetY + self.preview.getHeight() > self.engine.getHeight()):
            return ToolResult(ToolResult.UH_OH, self.preview.cost)

        if self.engine.budget.funds < self.preview.cost:
            return ToolResult(ToolResult.INSUFFICIENT_FUNDS, self.preview.cost)

        anyFound = False
        for y in xrange(len(self.preview.tiles)):
            for x in xrange(len(self.preview.tiles[0])):
                c = self.preview.tiles[y][x]
                if c != CLEAR:
                    self.engine.setTile(self.originX + x - self.preview.offsetX,
                                        self.originY + y - self.preview.offsetY,
                                        c)
                    anyFound = True

        for sound in set(self.preview.sounds):  # only do unique sounds
            self.engine.makeSound(sound)

        if anyFound and self.preview.cost != 0:
            self.engine.spend(self.preview.cost)
            return ToolResult(ToolResult.SUCCESS, self.preview.cost)
        else:
            return ToolResult(self.preview.toolResult, self.preview.cost)
