'''
Created on Oct 24, 2015

@author: chris
'''
from random import randint

import micropolistool
from toolStroke import ToolStroke
from translatedToolEffect import TranslatedToolEffect
from tileConstants import (isZoneCenter, getZoneSizeFor, isOverWater, RIVER, DIRT,
                            CLEAR, RADTILE, TINYEXP)


class Bulldozer(ToolStroke):
    def __init__(self, engine, xPos, yPos):
        super(Bulldozer, self).__init__(engine,
                                        micropolistool.types['BULLDOZER'],
                                        xPos, yPos)

    def applyArea(self, eff):
        b = self.getBounds()

        # scan selection area for rubble, forest, etc..
        for y in xrange(b.height):
            for x in xrange(b.width):
                subEff = TranslatedToolEffect(eff, b.x + x, b.y + y)
                if self.engine.isTileDozeable(subEff):
                    self.dozeField(subEff)

        # scan selection area for zones..
        for y in xrange(b.height):
            for x in xrange(b.width):
                if isZoneCenter(eff.getTile(b.x + x, b.y + y)):
                    self.dozeZone(TranslatedToolEffect(eff, b.x + x, b.y + y))



    def dozeZone(self, eff):
        curTile = eff.getTile(0, 0)

        assert isZoneCenter(curTile)

        dim = getZoneSizeFor(curTile)
        assert dim is not None
        assert dim.width >= 3
        assert dim.height >= 3

        eff.spend(1)

        # make sounds here
        '''if dim.width * dim.height < 16:
            eff.'''

        self.putRubble(TranslatedToolEffect(eff, -1, -1), dim.width, dim.height)

    def dozeField(self, eff):
        tile = eff.getTile(0, 0)

        if isOverWater(tile):
            eff.setTile(0, 0, RIVER)
        else:
            eff.setTile(0, 0, DIRT)

        self.fixZone(eff)
        eff.spend(1)

    def putRubble(self, eff, w, h):
        for yy in xrange(h):
            for xx in xrange(w):
                tile = eff.getTile(xx, yy)
                if tile == CLEAR:
                    continue

                if tile != RADTILE and tile != DIRT:
                    z = 0 if self.inPreview else randint(0,2)
                    nTile = TINYEXP + z
                    eff.setTile(xx, yy, nTile)

        self.fixBorder(eff, w, h)