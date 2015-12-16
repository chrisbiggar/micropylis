'''
Created on Dec 14, 2015

@author: chris
'''
from pyglet.text import Label

LEFT_ALIGN,CENTRE_ALIGN,RIGHT_ALIGN = range(3)


class VerticalLayout(object):
    def __init__(self):
        pass


class LayoutItem(object):
    def __init__(self):
        pass
    
    def layout(self):
        pass
    

class LayoutLabel(LayoutItem,Label):
    def __init__(self, parentFrame, alignment):
        super(LayoutLabel,self).__init__()
        self.parentFrame = parentFrame
        self.alignment = alignment
    
    def layout(self):
        if self.alignment == RIGHT_ALIGN:
            self.x = self.parentFrame.x + self.parentFrame.width - self.parentFrame.border\
                                    - self.content_width
        self.y = self.parentFrame.y + 220 + 2 + self.content_height
        


class LayoutFrame(object):
    def __init__(self, items=None):
        if items is not None:
            assert isinstance(items, list)
            self._items = items
        else:
            self._items = list()
        
    def addItem(self, item):
        self._items.append(item)
        
    def setFrameSize(self, width, height):
        self.frameWidth = width
        self.frameHeight = height
        
    def doLayout(self):
        for item in self._items:
            item.layout()
    
    
    
    
    
    
    