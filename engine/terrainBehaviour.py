'''
Created on Oct 19, 2015

@author: chris
'''
from random import randint

from engine import tileConstants
from engine.tileBehaviour import TileBehaviour
from engine.tileConstants import isCombustible, isZoneCenter, isConductive, isOverWater

FIRE, FLOOD, RADIOACTIVE, ROAD, RAIL, EXPLOSION = range(6)


class TerrainBehaviour(TileBehaviour):
    def __init__(self, city, b):
        super(TerrainBehaviour, self).__init__(city)
        self.behaviour = b
        self.TRAFFIC_DENSITY_TAB = [tileConstants.ROADBASE,
                                    tileConstants.LTRFBASE,
                                    tileConstants.HTRFBASE]

    def apply(self):
        if self.behaviour == FIRE:
            self.doFire()
        elif self.behaviour == FLOOD:
            self.doFlood()
        elif self.behaviour == RADIOACTIVE:
            self.doRadioactiveTile()
        elif self.behaviour == ROAD:
            self.doRoad()
        elif self.behaviour == RAIL:
            self.doRail()
        elif self.behaviour == EXPLOSION:
            self.doExplosion()
        else:
            assert False

    def doFire(self):
        self.city.firePop += 1

        if randint(0, 3) != 0:
            return

        dx = [0, 1, 0, -1]
        dy = [-1, 0, 1, 0]

        for dir in xrange(4):
            if randint(0, 7) == 0:
                x = self.x + dx[dir]
                y = self.y + dy[dir]
                if not self.city.testBounds(x, y):
                    continue

                tile = self.city.getTile(x, y)
                if isCombustible(tile):
                    if isZoneCenter(tile):
                        # self.city.kilZone()
                        # TODO make explosion
                        pass
                    self.city.setTile(x, y, tileConstants.FIRE + randint(0, 3))

        # TODO fire station coverage


        '''if (randint(0,rate) == 0) {
            city.setTile(xpos, ypos, (char)(RUBBLE + PRNG.nextInt(4)));
        }'''

    def doFlood(self):
        pass

    def doRadioactiveTile(self):
        if randint(0,4095) == 0:
            # radioactive decay
            self.city.setTile(self.x, self.y, tileConstants.DIRT)

    def doRoad(self):
        city = self.city

        city.roadTotal += 1

        if city.roadEffect < 30:
            # deteriorating roads
            if randint(0, 511) == 0:
                if not isConductive(self.tile):
                    if self.city.roadEffect < randint(0,31):
                        if isOverWater(self.tile):
                            self.city.setTile(self.x, self.y, tileConstants.RIVER)
                        else:
                            t = tileConstants.RUBBLE + randint(0,3)
                            self.city.setTile(self.x, self.y, t)
                        return

        if not isCombustible(self.tile):
            self.city.roadTotal += 4
            if self.doBridge():
                return

        if self.tile < tileConstants.LTRFBASE:
            tDen = 0
        elif self.tile < tileConstants.HTRFBASE:
            tDen = 1
        else:
            self.city.roadTotal += 1
            tDen = 2

        trafficDensity = self.city.getTrafficDensity(self.x, self.y)
        if trafficDensity < 64:
            newLevel = 0
        elif trafficDensity < 192:
            newLevel = 1
        else:
            newLevel = 2

        assert 0 <= newLevel < len(self.TRAFFIC_DENSITY_TAB)

        if tDen != newLevel:
            z = ((self.tile - tileConstants.ROADBASE & 15) +
                    self.TRAFFIC_DENSITY_TAB[newLevel])
            self.city.setTile(self.x, self.y, z)


    def doBridge(self):
        return False


    def doRail(self):
        self.city.railTotal += 1



    def doExplosion(self):
        self.city.setTile(self.x, self.y, tileConstants.RUBBLE + randint(0,3))
