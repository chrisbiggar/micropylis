import pyglet
from pyglet.gl import *
from pyglet.text import Label
from inspect import isframe
from util import createHollowRect


(HALIGN_LEFT,HALIGN_CENTER,HALIGN_RIGHT,
VALIGN_TOP,VALIGN_CENTER,VALIGN_BOTTOM) = range(6)



class Widget(object):
    '''
    Widget
    
    The most basic gui object which all others inherit from.
    '''
    def __init__(self, width=0, height=0):
        self.x = self.y = 0
        self.width = width
        self.height = height
        self.savedFrame = None
        self.active = True
        
    def setNeedsLayout(self):
        self.savedFrame.needsLayout = True
        
    def unFocus(self):
        pass
    
    def focus(self):
        pass
            
    def onMousePress(self, x, y, button, modifiers):
        pass
    def onMouseRelease(self, x, y, button, modifiers):
        pass
    def onMouseDrag(self, x, y, dx, dy, buttons, modifiers):
        pass
    def onMouseMotion(self, x, y, dx, dy):
        pass
    
    def delete(self):
        pass
        
    def enable(self):
        if not self.active:
            self.active = True
            self.savedFrame.setNeedsLayout()
    
    def disable(self):
        if self.active:
            self.active = False
            self.savedFrame.setNeedsLayout()
        
    def size(self, frame):
        self.savedFrame = frame
    
    def layout(self, x, y):
        self.x, self.y = x, y
    
    def hitTest(self, x, y):
        #print str(x) + " : " + str(self.x) + " : " + str(self.width)
        return x >= self.x and x < self.x + self.width and\
            y >= self.y and y < self.y + self.height
            
    def isExpandable(self):
        """
        Returns true if the widget can expand to fill available space.
        """
        return False
    
    def isClickable(self):
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
        #print width
        self.width, self.height = width, height

    def isExpandable(self):
        """Indicates the Spacer can be expanded"""
        return True

    def size(self, frame):
        """Spacer shrinks down to the minimum size for placement.

        @param savedFrame Dialog which contains us"""
        if frame is None:
            return
        Widget.size(self, frame)
        self.width, self.height = self.min_width, self.min_height
        

class ToolTip(object):
    '''
    A rectangle that contains text describing a gui item.
    
    When mouse hovers over an object for more than a second, if
    there is a tooltip assigned to that object, it will show.
    '''
    def __init__(self, x, y, text, batch, group):
        self.text = text
        self.batch = batch
        self.group = group
        self.x = x
        self.y = y
    
    def show(self):
        self.label = pyglet.text.Label(text=self.text,group=self.group+1)
        self.makeRect(self.x, self.y)
        

        
    def makeRect(self, x, y):
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
        x2 = x + self.width
        y2 = y + self.height
        c = (255, 200, 150, 255)
        colorData = []
        numVertices = 4
        for i in xrange(numVertices * len(c)):
            i2 = i % numVertices
            colorData.append(c[i2])
        self.bgRect = self.batch.add(4, GL_QUADS, self.group,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', colorData))
        
        
    def hide(self):
        self.bgRect.delete()
        self.bgRect = None
        self.label.delete()
        self.label = None
        
    def move(self, x, y):
        self.makeRect(x, y)
        self.label.x = x + 2
        self.label.y = y + 2
    
        
        
class LayoutGraphic(Widget):
    pass


class ButtonGraphic(LayoutGraphic):
    pass
        
        
class LayoutLabel(Widget):
    '''
    Wraps a pyglet Text Label and allows for layout.
    '''
    def __init__(self, frame, text="", toolTip=None, fontName=None, fontSize=None):
        super(LayoutLabel,self).__init__()
        self.savedFrame = frame
        self.text = text
        self.label = None
        self.fontName = fontName
        self.fontSize = fontSize
        self.toolTip = toolTip
        
    def delete(self):
        if self.label is not None:
            self.label.delete()
            self.label = None
            #print 'delete: ' + self.text
    
    def layout(self, x, y):
        Widget.layout(self, x, y)
        #print self.text,x,y
        if self.label is not None:
            #print self.label.text,x,y
            font = self.label.document.get_font()
            self.label.x = x
            self.label.y = y - font.descent
        
        
    def set_text(self, text):
        #print text
        self.text = text
        self.delete()
        #print "set text: " + text
        if self.savedFrame is not None:
            self.savedFrame.setNeedsLayout()

    def size(self, frame):
        if frame is None:
            return
        Widget.size(self, frame)
        if self.label is None:
            #print self.text
            #print "create: " + self.text
            self.group = self.savedFrame.fgGroup
            self.label = Label(self.text,
                               batch=self.savedFrame.batch,
                               group=self.savedFrame.fgGroup,
                               font_name=self.fontName,
                               font_size=self.fontSize)
            
            font = self.label.document.get_font()
            self.width = self.label.content_width
            self.height = font.ascent - font.descent
            
            
class ButtonLabel(LayoutLabel):
    '''
    Text Label that is clickable and will evoke an action.
    
    '''
    def __init__(self, frame, 
                 text=None, 
                 fontName=None, 
                 fontSize=None,
                 action=None):
        super(ButtonLabel,self).__init__(frame, 
                                         text=text, 
                                         fontName=fontName,
                                         fontSize=fontSize)
        self.action = action
        self.border = None
        self.color = (255,255,255,255)
        self.pressedColor = (0,0,0,255)
        self.borderColor = (255,255,255,255)
        self.pressed = False
        
    def focus(self):
        self.setBorder(createHollowRect(self.x - 4, self.y - 2, 
                                       self.label.content_width + 6, 
                                       self.label.content_height + 2, 
                                       self.borderColor, 
                                       self.savedFrame.batch, 
                                       self.savedFrame.fgGroup))

    def unFocus(self):
        self.label.color = self.color
        self.setBorder()
        self.pressed = False
        
    def onMousePress(self, x, y, button, modifiers):
        self.pressed = True
        self.label.color = self.pressedColor
            
    def onMouseRelease(self, x, y, button, modifiers):
        if self.pressed and self.action is not None:
            self.action()
        self.label.color = self.color
        self.pressed = False
        
    def setBorder(self, border=None):
        if self.border:
            self.border.delete()
            self.border = None
        self.border = border
    

    
    def isClickable(self):
        return True
            
            
            
class Layout(Widget):
    ''' base class for all layouts '''
    pass


class VerticalLayout(Layout):    
    '''
    Lays out widgets in a vertical line
    '''
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
    
    def size(self, frame):
        if frame is None:
            return
        if len(self.content) < 2:
            height = 0
        else:
            height = -self.padding
        
        width = 0
        for item in self.content:
            item.size(frame)
            height += item.height + self.padding
            width = max(width, item.width)
        self.width, self.height = width,height
        
        self.expandable = [x for x in self.content if x.isExpandable()]
        

    def layout(self, x, y):
        super(VerticalLayout,self).layout(x, y)
        
        top = y + self.height
        if self.align == HALIGN_RIGHT:
            for item in self.content:
                item.layout(x + self.width - item.width - self.padding,
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
    '''
    Lays out widgets in a horizontal line
    '''
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
        #print self.expandable
        available = int((width - self.width) / len(self.expandable))
        remainder = height - self.height - len(self.expandable) * available
        for item in self.expandable:
            if remainder > 0:
                item.expand(item.width + available + 1, item.height)
                remainder -= 1
            else:
                item.expand(item.width + available, item.height)
        self.width = width
        
        
    
    def size(self, frame):
        if frame is None:
            return
        if len(self.content) < 2:
            width = 0
        else:
            width = -self.padding
        
        Widget.size(self, frame)
            
        height = 0
        for item in self.content:
            item.size(frame)
            width += item.width + self.padding
            
            height = max(height, item.height)
        self.width, self.height = width,height
        
        self.expandable = [x for x in self.content if x.isExpandable()]
    


class Frame(Widget):
    '''
    Container for gui objects
    
    '''
    def __init__(self, content=None):
        self.content = content
        self.batch = None
        super(Frame,self).__init__()

    def setNeedsLayout(self):
        if self.savedFrame is not None:
            self.savedFrame.setNeedsLayout()
    
    def expand(self, width, height):
        """
        Expand the spacer to fill the maximum space.

        @param width Available width
        @param height Available height
        """
        if self.content.is_expandable():
            self.content.expand(width, height)

    def is_expandable(self):
        """Indicates the Spacer can be expanded"""
        return True
    
    
    def size(self, frame):
        super(Frame,self).size(frame)
        self.batch = frame.batch
        if self.content is not None and self.active:
            self.content.size(self)
            
            # do we want this?
            self.width, self.height = self.content.width, self.content.height
        else:
            self.width = self.height = 0
        
        
    def layout(self, x, y):
        super(Frame,self).layout(x,y)
        self.content.layout(self.x,self.y)


class LayoutWindow():
    '''
    Window gui manager. 
    Passes mouse events to the intersecting widget.
    
    
    '''
    def __init__(self, content):
        self.content = content
        self.needsLayout = True
        self.focus = None
        self.cursor = None
        self.batch = pyglet.graphics.Batch()
        
    def setNeedsLayout(self):
        self.needsLayout = True
        
    def doLayout(self, width, height):
        self.needsLayout = False
        
        self.content.size(self)
        if self.content.is_expandable():
            self.content.expand(width, height)
        self.content.layout(0, 0)
        
        
    def getWidgetAtPoint(self, x, y):
        content = self.content
        while True:
            if isinstance(content, Layout):
                hit = False
                for item in content.content:
                    if item.hitTest(x,y):
                        hit = True
                        if isinstance(item, Layout):
                            content = item
                            break
                        if isinstance(item,Frame):
                            content = item.content
                            break
                        else:
                            return item
                if not hit:
                    return content
            else:
                return None
    
    
    def onMousePress(self, x, y, button, modifiers):
        widget = self.getWidgetAtPoint(x, y)
        if widget:
            widget.onMousePress(x,y,button,modifiers)
    
    def onMouseRelease(self, x, y, button, modifiers):
        widget = self.getWidgetAtPoint(x, y)
        if self.focus and not self.focus.hitTest(x,y):
            self.focus.unFocus()
            self.focus = None
        if widget:
            widget.onMouseRelease(x,y,button,modifiers)
    
    def onMouseDrag(self, x, y, dx, dy, buttons, modifiers):
        widget = self.getWidgetAtPoint(x, y)
        if widget:
            widget.onMouseDrag(x, y, dx, dy, buttons, modifiers)
    
    def onMouseMotion(self, x, y, dx, dy):
        widget = self.getWidgetAtPoint(x, y)
        if widget:
            if self.focus:
                self.focus.unFocus()
                self.focus = None
            widget.onMouseMotion(x, y, dx, dy)
            self.focus = widget
            widget.focus()

        #if widget.toolTip is not None:
        #    self.curToolTip = ToolTip(text=widget.toolTip)
        
    def update(self, width, height):
        if self.needsLayout:
            self.doLayout(width, height)
        
    def draw(self):
        self.batch.draw()






