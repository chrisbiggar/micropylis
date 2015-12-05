'''
Created on Aug 30, 2015

@author: chris
'''
import pyglet
from engine.tileConstants import LOMASK
from pyglet.image import TextureGrid,AbstractImage\
,AbstractImageSequence,TextureRegion,ImageException,UniformTextureSequence

class SizeNotAvaiableError(Exception):
    pass


class Limits(object):
    '''
    
    '''
    def __init__(self):
        self.min = None
        self.max = None
        
    def setMin(self, m):
        self.min = m
        
    def setMax(self, m):
        self.max = m
        
    def update(self, new):
        if self.min == None:
            self.min = new
            self.max = new
            return
        if new < self.min:
            self.min = new
        elif new > self.max:
            self.max = new
        
    def withinRange(self, x):
        if x >= self.min and x <= self.max:
            return True
        else:
            return False

'''
class TileImagesBySize

default tile size must be specified at creation
''' '''
class TileImagesBySize(object):
    def __init__(self, defaultSize):
        self._curTileImages = None
        self._limits = Limits()
        self._sizes = dict()
        self._addSize(TileImages(16))
        self._defaultSize = defaultSize
        self.setCurrentSize(defaultSize)
        
        
    def getTileImage(self, cell):
        return self._curTileImages.getTileImage(cell)
    
    def currentTileSize(self):
        return self._curTileImages.tileSize
        
    def _addSize(self, size):
        self._limits.update(size.tileSize)
        self._sizes[str(size.tileSize)] = size
        
    def setCurrentSize(self, size):
        try:
            self._curTileImages = self._sizes[str(size)]
            self._currentSize = size
        except KeyError:
            raise SizeNotAvaiableError()
        
    def defaultSize(self):
        self.setCurrentSize(self._defaultSize)
    
    def higherSize(self):
        new = self._currentSize * 2
        if self._limits.withinRange(new):
            self.setCurrentSize(new)
        
    def lowerSize(self):
        new = self._currentSize / 2
        if self._limits.withinRange(new):
            self.setCurrentSize(new)'''
            

class BorderedImageGrid(AbstractImage, AbstractImageSequence):
    '''An imaginary grid placed over an image allowing easy access to
    regular regions of that image.

    The grid can be accessed either as a complete image, or as a sequence
    of _images.  The most useful applications are to access the grid
    as a `TextureGrid`::

        image_grid = ImageGrid(...)
        texture_grid = image_grid.get_texture_sequence()

    or as a `Texture3D`::

        image_grid = ImageGrid(...)
        texture_3d = Texture3D.create_for_image_grid(image_grid)

    '''
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
            for row in range(self.rows):
                x = self.exterior_border
                for col in range(self.columns):
                    self._items.append(self.image.get_region(
                        x, y, self.item_width, self.item_height))
                    x += self.item_width + self.column_padding
                y += self.item_height + self.row_padding

    def __getitem__(self, index):
        self._update_items()
        if type(index) is tuple:
            row, column = index
            assert row >= 0 and column >= 0 and \
                   row < self.rows and column < self.columns
            return self._items[row * self.columns + column]
        else:
            return self._items[index]

    def __iter__(self):
        self._update_items()
        return iter(self._items)


class BorderedTextureGrid(TextureRegion, UniformTextureSequence):
    '''A texture containing a regular grid of texture regions.

    To construct, create an `ImageGrid` first::

        image_grid = ImageGrid(...)
        texture_grid = TextureGrid(image_grid)

    The texture grid can be accessed as a single texture, or as a sequence
    of `TextureRegion`.  When accessing as a sequence, you can specify
    integer indexes, in which the _images are arranged in rows from the
    bottom-left to the top-right::

        # assume the texture_grid is 3x3:
        current_texture = texture_grid[3] # get the middle-left image

    You can also specify tuples in the sequence methods, which are addressed
    as ``row, column``::

        # equivalent to the previous example:
        current_texture = texture_grid[1, 0]

    When using tuples in a slice, the returned sequence is over the
    rectangular region defined by the slice::

        # returns center, center-right, center-top, top-right _images in that
        # order:
        _images = texture_grid[(1,1):]
        # equivalent to
        _images = texture_grid[(1,1):(3,3)]

    '''
    items = ()
    rows = 1
    columns = 1
    item_width = 0
    item_height = 0

    def __init__(self, grid, exterior_border=1):
        image = grid.get_texture()
        if isinstance(image, TextureRegion):
            owner = image.owner
        else:
            owner = image

        super(BorderedTextureGrid, self).__init__(
            image.x, image.y, image.z, image.width, image.height, owner)
        
        items = []
        y = exterior_border
        for row in range(grid.rows):
            x = exterior_border
            for col in range(grid.columns):
                items.append(
                    self.get_region(x, y, grid.item_width, grid.item_height))
                x += grid.item_width + grid.column_padding
            y += grid.item_height + grid.row_padding

        self.items = items
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
                assert row1 >= 0 and col1 >= 0 and \
                       row1 < self.rows and col1 < self.columns

                if type(index.stop) is tuple:
                    row2, col2 = index.stop
                elif type(index.stop) is int:
                    row2 = index.stop // self.columns
                    col2 = index.stop % self.columns
                assert row2 >= 0 and col2 >= 0 and \
                       row2 <= self.rows and col2 <= self.columns

                result = []
                i = row1 * self.columns
                for row in range(row1, row2):
                    result += self.items[i+col1:i+col2]
                    i += self.columns
                return result
        else:
            if type(index) is tuple:
                row, column = index
                assert row >= 0 and column >= 0 and \
                       row < self.rows and column < self.columns
                return self.items[row * self.columns + column]
            elif type(index) is int:
                return self.items[index]

    def __setitem__(self, index, value):
        if type(index) is slice:
            for region, image in zip(self[index], value):
                if image.width != self.item_width or \
                   image.height != self.item_height:
                    raise ImageException('Image has incorrect dimensions')
                image.blit_into(region, image.anchor_x, image.anchor_y, 0)
        else:
            image = value
            if image.width != self.item_width or \
               image.height != self.item_height:
                raise ImageException('Image has incorrect dimensions')
            image.blit_into(self[index], image.anchor_x, image.anchor_y, 0)

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)
    
    

        

'''
class TileImages
Makes available the individual images for each tile in a set.
Images are loaded from a given filename in sequential fashion, and are
referenced by their index into that sequence.
'''
class TileImages(object):
    def __init__(self, tileSize, padding=2):
        self.tileSize = tileSize
        self.padding = padding
        self._tileSheetFilename = 'res/tiles.png'
        self._tiles = self.loadTileImages()
        
    def loadTileImages(self):
        tileSheet = pyglet.image.load(self._tileSheetFilename)
        rows = tileSheet.height  / (self.tileSize + self.padding)
        columns = tileSheet.width / (self.tileSize + self.padding)
        return BorderedTextureGrid(
                            BorderedImageGrid(tileSheet, rows, columns,
                                                   row_padding=self.padding,
                                                   column_padding=self.padding))
    
    def getTileImage(self, cell):
        # low 10 bits give tile index number
        return self._tiles[(cell & LOMASK) % len(self._tiles)]












