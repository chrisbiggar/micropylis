'''
Created on Aug 30, 2015

@author: chris
'''
from __future__ import division

import pyglet
from pyglet.image import (TextureGrid, AbstractImage,
    AbstractImageSequence, TextureRegion, UniformTextureSequence,
                          Animation, AnimationFrame)

from engine.tileConstants import LOMASK, isAnimated, getTileBehaviour
import engine.tiles as tiles
from util.orderedSet import OrderedSet

'''
BorderedImageGrid

Extends pyglet's imagegrid class functionality to allow for borders
of a specific size around the specified source image edges.
'''


class BorderedImageGrid(AbstractImage, AbstractImageSequence):
    EXTERIOR_BORDER = 1
    _items = ()
    _texture_grid = None

    def __init__(self, image, rows, columns,
                 item_width=None, item_height=None,
                 row_padding=0, column_padding=0,
                 exterior_border=1):
        '''Construct a grid for the given image.

        You can specify parameters for the grid, for example setting
        the padding between cells.  Grids are always aligned to the 
        bottom-left corner of the image.

        :Parameters:
            `image` : AbstractImage
                Image over which to construct the grid.
            `rows` : int
                Number of rows in the grid.
            `columns` : int
                Number of columns in the grid.
            `item_width` : int
                Width of each column.  If unspecified, is calculated such
                that the entire image width is used.
            `item_height` : int
                Height of each row.  If unspecified, is calculated such that
                the entire image height is used.
            `row_padding` : int
                Pixels separating adjacent rows.  The padding is only
                inserted between rows, not at the edges of the grid.
            `column_padding` : int
                Pixels separating adjacent columns.  The padding is only 
                inserted between columns, not at the edges of the grid.
        '''
        super(BorderedImageGrid, self).__init__(image.width, image.height)

        if item_width is None:
            item_width = \
                (image.width - column_padding * (columns - 1) - exterior_border) // columns
        if item_height is None:
            item_height = \
                (image.height - row_padding * (rows - 1) - exterior_border) // rows
        self.image = image
        self.rows = rows
        self.columns = columns
        self.item_width = item_width
        self.item_height = item_height
        self.row_padding = row_padding
        self.column_padding = column_padding
        self.exterior_border = exterior_border

    def get_texture(self, rectangle=False, force_rectangle=False):
        return self.image.get_texture(rectangle, force_rectangle)

    def get_image_data(self):
        return self.image.get_image_data()

    def get_texture_sequence(self):
        if not self._texture_grid:
            self._texture_grid = TextureGrid(self)
        return self._texture_grid

    def __len__(self):
        return self.rows * self.columns

    def _update_items(self):
        if not self._items:
            self._items = []
            y = self.exterior_border
            for row in xrange(self.rows):
                x = self.exterior_border
                for col in xrange(self.columns):
                    self._items.append(self.image.get_region(
                        int(x), int(y), self.item_width, self.item_height))
                    x += self.item_width + self.column_padding
                y += self.item_height + self.row_padding

    def __getitem__(self, index):
        self._update_items()
        if type(index) is tuple:
            row, column = index
            assert (0 <= row < self.rows and
                    0 <= column < self.columns)
            return self._items[row * self.columns + column]
        else:
            return self._items[index]

    def __iter__(self):
        self._update_items()
        return iter(self._items)


class TileAnimation(Animation):
    def __init__(self, sequence, loop):
        frames = [AnimationFrame(image, 1) for image in sequence]
        if not loop:
            frames[-1].duration = None
        super(TileAnimation,self).__init__(frames)
        self.curFrameNum = 0
        self.loop = loop

    def reset(self):
        self.curFrameNum = 0

    def getCurrentFrameDuration(self):
        return self.frames[self.curFrameNum].duration

    def getCurrentFrameImg(self):
        return self.frames[self.curFrameNum].image

    def update(self):
        self.curFrameNum += 1
        if self.curFrameNum >= len(self.frames):
            self.curFrameNum = 0


'''
BorderedAnimatedTextureGrid

Extends BorderedImageGrid to store image as texture and uses engine.tiles.Tiles to
process animations to store them as pyglet animations.
Due to pyglet's sprite module treating images generically, one does not
have to know whether they have retreived a textureregion or animation when using this class.
'''

class BorderedAnimatedTextureGrid(TextureRegion, UniformTextureSequence):
    items = ()
    rows = 1
    columns = 1
    item_width = 0
    item_height = 0

    def __init__(self, animationDelay, grid,
                 exterior_border=1, flipTilesVert=False):
        image = grid.get_texture()
        if isinstance(image, TextureRegion):
            owner = image.owner
        else:
            owner = image

        super(BorderedAnimatedTextureGrid, self).__init__(
            image.x, image.y, image.z, image.width, image.height, owner)

        textureItems = []
        y = exterior_border
        tileNum = 0
        for row in xrange(grid.rows):
            x = exterior_border
            for col in xrange(grid.columns):
                region = self.get_region(x, y, grid.item_width, grid.item_height)
                if flipTilesVert:
                    region = region.get_transform(flip_y=True)
                textureItems.append(region)
                x += grid.item_width + grid.column_padding
            y += grid.item_height + grid.row_padding

        # process animations
        tileNum = 0
        finalItems = [0 for tNum in xrange(len(textureItems))]
        for row in xrange(grid.rows):
            for col in xrange(grid.columns):
                spec = tiles.get(tileNum)
                if spec.animNext is None:
                    finalItems[tileNum] = textureItems[tileNum]
                else:
                    frames = []
                    frameNums = []
                    stopFrame = tileNum
                    curFrame = tileNum
                    firstFrame = None
                    while True:
                        if firstFrame is None:
                            firstFrame = curFrame
                        frames.append(textureItems[curFrame])
                        frameNums.append(curFrame)
                        if spec.animNext is None:
                            #print "stop " + str(tileNum) + " " + str(spec.tileNum) + " " + str(curFrame)
                            curFrame += 1
                            stopFrame = curFrame
                        else:
                            curFrame = spec.animNext.tileNum
                        if curFrame == stopFrame:
                            break
                        spec = tiles.get(curFrame)

                    f = min(frameNums)
                    if f != tileNum:
                        finalItems[tileNum] = finalItems[f]
                    else:
                        loop = True if tileNum == stopFrame else False
                        finalItems[tileNum] = TileAnimation(frames, loop)
                    #print tileNum,finalItems[tileNum]
                tileNum += 1

        self.items = finalItems
        self.rows = grid.rows
        self.columns = grid.columns
        self.item_width = grid.item_width
        self.item_height = grid.item_height
        self.exterior_border = exterior_border

    def get(self, row, column):
        return self[(row, column)]

    def __getitem__(self, index):
        if type(index) is slice:
            if type(index.start) is not tuple and \
                            type(index.stop) is not tuple:
                return self.items[index]
            else:
                row1 = 0
                col1 = 0
                row2 = self.rows
                col2 = self.columns
                if type(index.start) is tuple:
                    row1, col1 = index.start
                elif type(index.start) is int:
                    row1 = index.start // self.columns
                    col1 = index.start % self.columns
                assert (0 <= row1 < self.rows and
                        0 <= col1 < self.columns)

                if type(index.stop) is tuple:
                    row2, col2 = index.stop
                elif type(index.stop) is int:
                    row2 = index.stop // self.columns
                    col2 = index.stop % self.columns
                assert (0 <= row2 < self.rows and
                        0 <= col2 < self.columns)

                result = []
                i = row1 * self.columns
                for row in xrange(row1, row2):
                    result += self.items[i + col1:i + col2]
                    i += self.columns
                return result
        else:
            if type(index) is tuple:
                row, column = index
                assert (0 <= row < self.rows and
                        0 <= column < self.columns)
                return self.items[row * self.columns + column]
            elif type(index) is int:
                return self.items[index]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)


'''
TileImageLoader

Loads the specified tile sheet into a BorderedAnimatedTextureGrid.
Allows access by tile number with getTIleImage(cell)

Tiles image returned will either be an animation or textureregion.
'''


class TileImageLoader(object):
    DEFAULT_ANIMATION_DELAY = 0.2

    def __init__(self, fileName, tileSize, flipTilesVert=False, padding=0):
        self.tileSize = tileSize
        self.flipTilesVert = flipTilesVert
        self.padding = padding
        assert isinstance(fileName, str)
        self._tileSheetFilename = fileName
        self._tiles = self.loadTileImages()
        animations = []
        for t in self._tiles.items:
            if isinstance(t,TileAnimation):
                animations.append(t)
        self.animations = OrderedSet(animations)

    def getAnimations(self):
        return self.animations

    def getTexture(self):
        return self._tiles.texture

    def loadTileImages(self):
        tileSheet = pyglet.resource.image(self._tileSheetFilename)
        rows = tileSheet.height // (self.tileSize + self.padding)
        columns = tileSheet.width // (self.tileSize + self.padding)
        return BorderedAnimatedTextureGrid(
            self.DEFAULT_ANIMATION_DELAY,
            BorderedImageGrid(tileSheet, rows, columns,
                              row_padding=self.padding,
                              column_padding=self.padding),
            flipTilesVert=self.flipTilesVert)

    def getTileImage(self, cell):
        # low 10 bits give tile index number
        return self._tiles[(cell & LOMASK) % len(self._tiles)]
