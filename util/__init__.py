import struct
import pyglet
from pyglet.gl import GL_LINE_STRIP,GL_QUADS


''' 

#  misc functions
'''
def tupleFromString(string):
    l = string.lstrip('(').rstrip(')').split(',')
    intL = []
    for x in l:
        intL.append(int(x))
    return tuple(intL)
    
    
def create2dArray(width, height, fillValue=0):
    return [[fillValue for y in range(height)] for x in range(width)]

def writeShort(aFile, short):
    pass

def writeInt(aFile, int_):
    pass

def readShort(aFile):
    '''map is stored big endian'''
    return struct.unpack('>H',aFile.read(2))[0]

def readInt(aFile):
    '''map is stored big endian'''
    return struct.unpack('>I', aFile.read(4))[0]

def createHollowRect(x,y,width,height,color,batch,group):
    '''
    create a hollow rect vertex list and add to given batch group.
    
    uses gl linestips
    '''
    x2 = x + width
    y2 = y + height
    numVertices = 5
    colorData = []
    for i in xrange(numVertices * len(color)):
        i2 = i % 4
        colorData.append(color[i2])
    return batch.add(numVertices,
                                GL_LINE_STRIP,
                                group,
                                ('v2f', [x, y, x2, y, x2, y2, x, y2, x, y]),
                                ('c4B', colorData))

def createRect(x,y,width,height,color,batch,group):
    '''
    create a solid rect vertex list and add to batch given
    '''
    x2 = x + width
    y2 = y + height
    colorData = []
    numVertices = 4
    for i in xrange(numVertices * len(color)):
        i2 = i % numVertices
        colorData.append(color[i2])
    return batch.add(numVertices, GL_QUADS, group,
                             ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                             ('c4B', colorData))
    
def createLine(x,y,x2,y2,color,width,batch,group):
    '''
    create a single line vertex list and add to batch given
    '''
    colorData = []
    numVertices = 2
    for i in xrange(numVertices * len(color)):
        i2 = i % numVertices
        colorData.append(color[i2])
    return batch.add(numVertices, GL_LINE_STRIP,
                     group,
                     ('v2f', [x,y,x2,y2]),
                     ('c4B', colorData))