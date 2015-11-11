'''
Created on Oct 29, 2015

@author: chris
'''
from collections import deque
from math import floor
import pyglet
from pyglet.text import Label
from pyglet.text.layout import TextLayout
from pyglet.text.document import UnformattedDocument, FormattedDocument
from pyglet.gl import *

bgGroup = pyglet.graphics.OrderedGroup(1)
mgGroup = pyglet.graphics.OrderedGroup(2)
fgGroup = pyglet.graphics.OrderedGroup(3)

MSG_SHOW_TIME = 10 # in seconds


class Message(object):
    def __init__(self, msg, startTime):
        self.string = msg
        self.time = int(startTime)
    
    def isExpired(self, dt):
        return int(dt) > self.time + MSG_SHOW_TIME
    

class MessageQueue(object):
    def __init__(self):
        self.msgs = deque(maxlen=12)
        self.dt = 0
        self.secs = 0
    
    def create(self, batch, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        x2 = x + self.width
        y2 = y + self.height
        c = (90,20,65,255)
        
        self.doc = UnformattedDocument()
        self.layout = TextLayout(self.doc,
                                         width = width,
                                         height = height,
                                         batch=batch,
                                         group=fgGroup,
                                         multiline=True)
        self.layout.x = x
        self.layout.y = y
        self.doc.set_style(0,0,dict(font_name='Arial', font_size=12))
        self.bgRect = batch.add(4, GL_QUADS, mgGroup,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', [c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]
                                    ,c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]]))
        
    def _resetDoc(self):
        self.doc.text = ""
        for item in self.msgs:
            self.doc.text += item.string + "\n"
    
    def addMessage(self, msg):
        self.msgs.append(Message(msg, floor(self.secs)))
        self._resetDoc()
        if self.layout.content_height > self.height:
            self.msgs.popleft()
            self._resetDoc()
            
    def update(self, dt):
        self.dt += dt
        secs = floor(self.dt)
        if secs != self.secs:
            # only check for expiries once a second
            self.secs = secs
            toRemove = []
            for item in self.msgs:
                if item.isExpired(secs):
                    toRemove.append(item)
            if len(toRemove) > 0:
                for item in toRemove:
                    self.msgs.remove(item)
                self._resetDoc()



class InfoPane(object):
    def __init__(self, engine, x, y, width, height):
        self.engine = engine
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = 10
        self.batch = pyglet.graphics.Batch()
        self.layout()
        self.reset(engine)
        
    def reset(self, engine):
        self.engine = engine
        engine.push_handlers(self)
        self.on_funds_changed()
        
    def layout(self):
        self.msgs = MessageQueue()
        self.msgs.create(self.batch, self.x + self.border, self.border, 
                         self.width - 20, 200)
        self.fundsLabel = Label(x=self.x + self.width - 146,
                                y=self.y + self.height - 20,
                                batch=self.batch,
                                group=fgGroup)
        self.createBackground()

    def createBackground(self):
        x = self.x
        y = self.y
        x2 = self.x + self.width
        y2 = self.x + self.height
        c = (0,75,70,255)
        self.bg = self.batch.add(4, GL_QUADS, bgGroup,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', [c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]
                                    ,c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]]))
        
    
    def addInfoMessage(self, msg):
        self.msgs.addMessage(msg)
        
    def on_funds_changed(self):
        self.fundsLabel.text = "Treasury: $" + str(self.engine.budget.funds)
        # right-align label, respecting border
        self.fundsLabel.x = self.x + self.width - self.border\
                                - self.fundsLabel.content_width
    
    def update(self, dt):
        self.msgs.update(dt)
    