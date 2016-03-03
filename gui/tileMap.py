import math

from pyglet.gl import *
from pyglet.graphics import vertexdomain
from pyglet.graphics.vertexdomain import VertexList

from .tileImageLoader import TileAnimation
from util import create2dArray


TILESIZE = 16

'''
    Uses a vertexdomain and vertexlists to render the tilemap.
    Made for efficient updating.
'''


class TileMapRenderer(object):
    def __init__(self, tileImagesLoader, group):
        self._engine = None
        self.tileImagesLoader = tileImagesLoader
        self.texture = self.tileImagesLoader.getTexture()
        self.animations = self.tileImagesLoader.getAnimations()

        self.animated = dict()
        self.visibleAnimated = dict()

        self.domain = vertexdomain.create_domain(*('v2i', 't3f'))
        self.nullDomain = None
        self.group = group

        self.regionSize = 6
        self.regions = None
        self.regionsVisible = None

    def _add(self, count, vertices, texCoords):
        # Create vertex list and initialize
        vlist = self.domain.create(count)
        vlist._set_attribute_data(0, vertices)
        vlist._set_attribute_data(1, texCoords)
        return vlist

    def resetEng(self, eng):
        self._engine = eng
        self.animated = dict()
        self.visibleAnimated = dict()
        del self.domain
        self.domain = vertexdomain.create_domain(*('v2i', 't3f'))
        self.nullDomain = vertexdomain.create_domain(*('v2i', 't3f'))

        if self.regions is not None:
            for row in xrange(self.rows):
                for column in xrange(self.columns):
                    self.regions[row][column].delete()

        if eng is None:
            return
        self.rows = int(math.ceil(float(eng.getWidth()) / self.regionSize))
        self.columns = int(math.ceil(float(eng.getHeight()) / self.regionSize))

        self.regions = create2dArray(self.rows, self.columns)
        self.regionsVisible = create2dArray(self.rows, self.columns, True)
        for row in xrange(self.rows):
            for column in xrange(self.columns):
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
                        if eng.testBounds(x, y):
                            vertices.extend([x1, y1, x2, y1, x2, y2, x1, y2])
                            tImg = self.tileImagesLoader.getTileImage(eng.getTile(x, y))
                            try:
                                texCoords.extend(tImg.tex_coords)
                            except AttributeError:
                                assert isinstance(tImg, TileAnimation)
                                texCoords.extend(tImg.frames[0].image.tex_coords)
                                self.visibleAnimated[(x, y)] = tImg
                        else:
                            vertices.extend([0, 0, 0, 0, 0, 0, 0, 0])
                            texCoords.extend([0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.])
                self.regions[row][column] = self._add(len(vertices) // 2, vertices, texCoords)

    def setVisibleRegion(self, screenX, screenY, width, height):
        screenX = int(screenX)
        screenY = int(screenY)
        left = max(screenX // TILESIZE // self.regionSize - 1, 0)
        right = min((screenX + int(width)) / TILESIZE // self.regionSize + 2, len(self.regions))
        top = max(screenY // TILESIZE // self.regionSize - 1, 0)
        bottom = min((screenY + int(height)) // TILESIZE // self.regionSize + 2, len(self.regions[0]))

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
                for iX in xrange(sX, sX + self.regionSize):
                    for iY in xrange(sY, sY + self.regionSize):
                        if self._engine.testBounds(iX, iY):
                            self.setTile(iX, iY, self._engine.getTile(iX, iY))
                            if (iX, iY) in self.animated:
                                self.visibleAnimated[(iX, iY)] = self.animated.pop((iX, iY))
                self.regions[x][y].migrate(self.domain)
            else:
                sX = x * self.regionSize
                sY = y * self.regionSize
                for iX in xrange(sX, sX + self.regionSize):
                    for iY in xrange(sY, sY + self.regionSize):
                        if (iX, iY) in self.visibleAnimated:
                            self.animated[(iX, iY)] = self.visibleAnimated.pop((iX, iY))
                self.regions[x][y].migrate(self.nullDomain)

    def resetTile(self, x, y):
        self.setTile(x, y, self._engine.getTile(x, y))

    def setTile(self, x, y, tileNum):
        rX = x // self.regionSize
        rY = y // self.regionSize
        tImg = self.tileImagesLoader.getTileImage(tileNum)

        try:
            curFrameImg = tImg.getCurrentFrameImg()
            anim = True
        except AttributeError:
            anim = False

        if anim:
            if not self.regionsVisible[rX][rY]:
                self.animated[(x, y)] = tImg
                return
            else:
                self.visibleAnimated[(x, y)] = tImg
            if not tImg.loop:
                tImg.reset()
            tImg = curFrameImg
        else:
            if self.regionsVisible[rX][rY]:
                try:
                    del self.visibleAnimated[(x, y)]
                except KeyError:
                    pass
            else:
                try:
                    del self.animated[(x, y)]
                except KeyError:
                    pass
        self._setTile((x, y), tImg)

    def _setTile(self, pos, texRegion):
        i = ((pos[0] % self.regionSize) * self.regionSize + (pos[1] % self.regionSize)) * 12
        self.regions[pos[0] // self.regionSize][pos[1] // self.regionSize].tex_coords[i:i+12] = texRegion.tex_coords

    def update(self, dt):
        for anim in self.animations:
            anim.update()
        finished = []
        for key, anim in self.visibleAnimated.items():
            if not anim.loop and anim.getCurrentFrameDuration() is None:
                finished.append(key)
                continue
            self._setTile(key, anim.getCurrentFrameImg())
        for key in finished:
            del self.visibleAnimated[key]

    def draw(self):
        self.group.set_state()
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        self.domain.draw(GL_QUADS)
        glDisable(self.texture.target)
        self.group.unset_state()
