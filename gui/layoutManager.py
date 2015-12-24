'''
Created on Dec 14, 2015

@author: chris
'''
from pyglet.text import Label

(HALIGN_LEFT,HALIGN_CENTER,HALIGN_RIGHT,
VALIGN_TOP,VALIGN_CENTER,VALIGN_BOTTOM) = range(6)



class Widget(object):
    def __init__(self, width=0, height=0):
        self.x = self.y = 0
        self.width = width
        self.height = height
        self.savedDialog = None
        
    def size(self, dialog):
        self.savedDialog = dialog
    
    def layout(self, x, y):
        self.x, self.y = x, y
    
    def hitTest(self, x, y):
        return x >= self.x and x < self.x + self.width and\
            y >= self.y and y < self.y + self.height
            
    def isExpandable(self):
        """
        Returns true if the widget can expand to fill available space.
        """
        return False

class Spacer(Widget):
    """
    A Spacer is an empty widget that expands to fill space in layouts.
    Use Widget if you need a fixed-sized spacer.
    """
    def __init__(self, width=0, height=0):
        """
        Creates a new Spacer.  The width and height given are the minimum
        area that we must cover.

        @param width Minimum width
        @param height Minimum height
        """
        Widget.__init__(self)
        self.min_width, self.min_height = width, height

    def expand(self, width, height):
        """
        Expand the spacer to fill the maximum space.

        @param width Available width
        @param height Available height
        """
        self.width, self.height = width, height

    def isExpandable(self):
        """Indicates the Spacer can be expanded"""
        return True

    def size(self, dialog):
        """Spacer shrinks down to the minimum size for placement.

        @param dialog Dialog which contains us"""
        if dialog is None:
            return
        Widget.size(self, dialog)
        self.width, self.height = self.min_width, self.min_height
        
        
        
class LayoutLabel(Widget):
    def __init__(self, parentFrame, text=""):
        super(LayoutLabel,self).__init__()
        self.parentFrame = parentFrame
        self.text = text
        self.label = None
        
    def delete(self):
        if self.label is not None:
            self.label.delete()
            self.label = None
    
    def layout(self, x, y):
        Widget.layout(self, x, y)
        #print self.text,x,y
        if self.label is not None:
            #print self.label.text,x,y
            font = self.label.document.get_font()
            self.label.x = x
            self.label.y = y - font.descent
        
        
    def set_text(self, text):
        self.text = text
        self.delete()
        #print "set text: " + text
        if self.savedDialog is not None:
            self.savedDialog.setNeedsLayout()

    def size(self, dialog):
        if dialog is None:
            return
        Widget.size(self, dialog)
        if self.label is None:
            self.label = Label(self.text,
                               batch=self.parentFrame.batch,
                               group=self.parentFrame.fgGroup)
            
            font = self.label.document.get_font()
            self.width = self.label.content_width
            self.height = font.ascent - font.descent 

class VerticalLayout(Widget):
    def __init__(self, content=[], align=HALIGN_CENTER, padding=5):
        super(VerticalLayout,self).__init__()
        self.align = align
        self.padding = padding
        self.content = content
    
    def delete(self):
        for item in self.content:
            item.delete()
        
    def is_expandable(self):
        """True if we contain expandable content."""
        return len(self.expandable) > 0
    
    def size(self, window):
        if window is None:
            return
        if len(self.content) < 2:
            height = 0
        else:
            height = -self.padding
        width = 0
        for item in self.content:
            item.size(window)
            height += item.height + self.padding
            width = max(width, item.width)
        self.width, self.height = width,height
        
    
    def layout(self, x, y):
        super(VerticalLayout,self).layout(x, y)
        
        top = y + self.height
        if self.align == HALIGN_RIGHT:
            for item in self.content:
                item.layout(x + self.width - item.width,
                            top - item.height)
                top -= item.height + self.padding
        elif self.align == HALIGN_CENTER:
            for item in self.content:
                item.layout(x + self.width/2 - item.width/2,
                            top - item.height)
                top -= item.height + self.padding
        else: # HALIGN_LEFT
            for item in self.content:
                item.layout(x, top - item.height)
                top -= item.height + self.padding
                
    def expand(self, width, height):
        """
        Expands to fill available vertical space.  We split available space
        equally between all spacers.
        """
        available = int((height - self.height) / len(self.expandable))
        remainder = height - self.height - len(self.expandable) * available
        for item in self.expandable:
            if remainder > 0:
                item.expand(item.width, item.height + available + 1)
                remainder -= 1
            else:
                item.expand(item.width, item.height + available)
        self.height = height
        self.width = width

    
class HorizontalLayout(VerticalLayout):
    def __init__(self, content=[], align=HALIGN_CENTER, padding=5):
        super(HorizontalLayout,self).__init__(content, align, padding)
    
    def layout(self, x, y):
        Widget.layout(self, x, y)
        
        # expand any expandable content to our height
        for item in self.content:
            if item.isExpandable() and item.height < self.height:
                item.expand(item.width, self.height)
                
        left = x
        if self.align == HALIGN_LEFT:
            for item in self.content:
                item.layout(left, y + self.height - item.height)
                left += item.width + self.padding
        elif self.align == HALIGN_CENTER:
            for item in self.content:
                item.layout(left, y + self.height/2 - item.height / 2)
                left += item.width + self.padding
                #print str(item) + str((item.x,item.y,item.width,item.height))
                
                
    def expand(self, width, height):
        available = int((width - self.width) / len(self.expandable))
        remainder = height - self.height - len(self.expandable) * available
        for item in self.expandable:
            if remainder > 0:
                item.expand(item.width + available + 1, item.height)
                remainder -= 1
            else:
                item.expand(item.width + available, item.height)
        self.width = width
        
        
    
    def size(self, window):
        if window is None:
            return
        if len(self.content) < 2:
            width = 0
        else:
            width = -self.padding
        height = 0
        for item in self.content:
            item.size(window)
            width += item.width + self.padding
            height = max(height, item.height)
        self.width, self.height = width,height
        self.expandable = [x for x in self.content if x.isExpandable()]
        #print "expandable: " + str(self.expandable)
        #print self.width,self.height
    


class Frame(Widget):
    def __init__(self, content=None):
        self.content = content
        super(Frame,self).__init__()

    def setNeedsLayout(self):
        if self.savedDialog is not None:
            self.savedDialog.setNeedsLayout()
    
    def expand(self, width, height):
        """
        Expand the spacer to fill the maximum space.

        @param width Available width
        @param height Available height
        """
        if self.content.is_expandable():
            self.content.expand(width, height)
        self.width, self.height = self.WIDTH, height

    def is_expandable(self):
        """Indicates the Spacer can be expanded"""
        return True
    
    
    def size(self, window):
        super(Frame,self).size(window)
        if self.content is not None:
            self.content.size(self)
            self.width, self.height = self.content.width, self.content.height
        else:
            self.width = self.height = 0
        
        
        self.width, self.height = self.WIDTH, window.height
        
    def layout(self, x, y):
        super(Frame,self).layout(x,y)
        self.content.layout(self.x,self.y)



class LayoutWindow(Widget):
    def __init__(self, window, content):
        super(LayoutWindow,self).__init__(window.width,
                                          window.height)
        self.savedDialog = window
        self.content = content
        self.needsLayout = True
        
    def expand(self, width, height):
        if self.content.is_expandable():
            self.content.expand(width, height)
        self.width = width
        self.height = height
        
        
    def size(self, window):
        if self.content is not None:
            self.content.size(self)
            self.width, self.height = self.content.width, self.content.height
        else:
            self.width = self.height = 0
        
        self.expand(window.width, window.height)
        
        
    def doLayout(self, window):
        self.needsLayout = False
        self.size(window)
        self.content.layout(self.x, self.y)
        
    def update(self, dt):
        if self.needsLayout:
            #print "do layout update"
            self.doLayout(self.savedDialog)
    
    def setNeedsLayout(self):
        self.needsLayout = True
    

    
    
    
    
    
    