import math

from pyglet.gl import *
from pyglet.graphics import vertexdomain
from pyglet.graphics.vertexdomain import VertexList

from tileImageLoader import TileAnimation
from util import create2dArray


TILESIZE = 16

'''
    Uses a vertexdomain and vertexlists to render the tilemap.
    Made for efficient updating.
'''


class TileMapRenderer(object):

    def __init__(self, tileImagesLoader, group):
        self.engine = None
        self.tileImagesLoader = tileImagesLoader
        self.animations = self.tileImagesLoader.getAnimations()
        self.domain = None
        self.nullDomain = None
        self.dt = 0
        self.group = group
        self.texture = self.tileImagesLoader.getTexture()
        self.regionSize = 6
        self.regions = None
        self.regionsVisible = None
        self.lastChangeX = self.lastChangeY = self.lastChangeWidth = self.lastChangeHeight = 0
        self.changeThreshold = TILESIZE * 6
        self.animatedTiles = dict()

    def _add(self, count, vertices, texCoords):
        # Create vertex list and initialize
        vlist = self.domain.create(count)
        vlist._set_attribute_data(0, vertices)
        vlist._set_attribute_data(1, texCoords)
        return vlist

    def reset(self, eng):
        self.engine = eng

        self.animatedTiles = dict()

        if eng is None:
            return

        self.domain = vertexdomain.create_domain(*('v2i', 't3f'))
        self.nullDomain = vertexdomain.create_domain(*('v2i', 't3f'))

        rows = int(math.ceil(float(eng.getWidth()) / self.regionSize))
        columns = int(math.ceil(float(eng.getHeight()) / self.regionSize))
        if self.regions is not None:
            for row in xrange(rows):
                for column in xrange(columns):
                    self.regions[row][column].delete()

        self.regions = create2dArray(rows, columns)
        self.regionsVisible = create2dArray(rows, columns, True)
        for row in xrange(rows):
            for column in xrange(columns):
                texCoords = []
                vertices = []
                sX = row * self.regionSize
                sY = column * self.regionSize
                for x in xrange(sX, sX + self.regionSize):
                    for y in xrange(sY, sY + self.regionSize):
                        x1 = int(x * TILESIZE)
                        y1 = int(y * TILESIZE)
                        x2 = int(x1 + TILESIZE)
                        y2 = int(y1 + TILESIZE)
                        vertices.extend([x1, y1, x2, y1, x2, y2, x1, y2])
                        if eng.testBounds(x, y):
                            texCoords.extend(self.tileImagesLoader.getTileImage(eng.getTile(x, y)).tex_coords)
                        else:
                            texCoords.extend([0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.])
                self.regions[row][column] = self._add(len(vertices) / 2, vertices, texCoords)
        # self._updateRegions()


    def setVisibleRegion(self, screenX, screenY, width, height):
        screenX = int(screenX)
        screenY = int(screenY)
        left = max(screenX / TILESIZE / self.regionSize - 1, 0)
        right = min((screenX + int(width)) / TILESIZE / self.regionSize + 2, len(self.regions))
        top = max(screenY / TILESIZE / self.regionSize - 1, 0)
        bottom = min((screenY + int(height)) / TILESIZE / self.regionSize + 2, len(self.regions[0]))

        changes = []
        for x in xrange(len(self.regions)):
            for y in xrange(len(self.regions[0])):
                if left <= x < right and top <= y < bottom:
                    if not self.regionsVisible[x][y]:
                        changes.append((x,y))
                        self.regionsVisible[x][y] = True
                elif self.regionsVisible[x][y]:
                    changes.append((x,y))
                    self.regionsVisible[x][y] = False
        self._updateRegions(changes)

    def _updateRegions(self, changes=None):
        if changes is None:
            changes = []
            num = 0
            for x in xrange(len(self.regions)):
                for y in xrange(len(self.regions[0])):
                    changes.append((x,y))

        for index in changes:
            x = index[0]
            y = index[1]
            if self.regionsVisible[x][y]:
                # update tiles:
                sX = x * self.regionSize
                sY = y * self.regionSize
                # print sX, sY
                for iX in xrange(sX, sX + self.regionSize):
                    for iY in xrange(sY, sY + self.regionSize):
                        if self.engine.testBounds(iX,iY):
                            self.setTile(iX, iY, self.engine.getTile(iX, iY))
                            # print iX,iY,self.engine.getTile(iX, iY)
                self.regions[x][y].migrate(self.domain)
            else:

                self.regions[x][y].migrate(self.nullDomain)

    def setTile(self, x, y, tileNum):
        rX = x / self.regionSize
        rY = y / self.regionSize
        if not self.regionsVisible[rX][rY]:
            return
        tImg = self.tileImagesLoader.getTileImage(tileNum)
        if isinstance(tImg, TileAnimation): # just for now. get rid of later for efficiency
            self.animatedTiles[(x, y)] = tImg
            if not tImg.loop:
                tImg.reset()
            tImg = tImg.getCurrentFrameImg()
        else:
            try:
                del self.animatedTiles[(x, y)]
            except KeyError:
                pass
        self._setTile(x, y, tImg)

    def _setTile(self, x, y, texRegion):
        rX = x / self.regionSize
        rY = y / self.regionSize
        i = ((x % self.regionSize) * self.regionSize + (y % self.regionSize)) * 12
        self.regions[rX][rY].tex_coords[i:i+12] = texRegion.tex_coords

    def update(self, dt):
        if self.dt >= 0.08:
            self.dt = 0
            for anim in self.animations:
                anim.update()
            finished = []
            num = 0
            for key, anim in self.animatedTiles.iteritems():
                x = key[0]
                y = key[1]
                if self.regionsVisible[x / self.regionSize][y / self.regionSize] is False:
                    continue
                if not anim.loop and anim.getCurrentFrameDuration() is None:
                    finished.append((x, y))
                    continue
                num += 1
                self._setTile(x, y, anim.getCurrentFrameImg())
            #print num
            for key in finished:
                del self.animatedTiles[key]
        self.dt += dt

    def draw(self):
        self.group.set_state()
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        self.domain.draw(GL_QUADS)
        glDisable(self.texture.target)
        self.group.unset_state()
