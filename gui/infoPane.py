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
    def __init__(self, num, msg, startTime, start):
        self.string = msg
        self.time = int(startTime)
        self.index = start
        self.num = num
    
    def isExpired(self, dt):
        return int(dt) > self.time + MSG_SHOW_TIME
    
    def __len__(self):
        return len(self.string)
    

'''
    displays messages to user. 
'''
class MessageQueue(object):
    def __init__(self, batch, width):
        self.batch = batch
        #self.msgs = deque(maxlen=12)
        self.msgs = list()
        self.dt = 0
        self.secs = 0
        self.bgRect = None
        self.doc = FormattedDocument()
        self.layout = TextLayout(self.doc,
                                     width=width,
                                     batch=batch,
                                     group=fgGroup,
                                     multiline=True)
        self.titleLabel = Label("City Messages",
                                   batch=self.batch,
                                   group=fgGroup)
        self.currentPos = 0
        self.numMsgs = 0
    
    def doLayout(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        x2 = x + self.width
        y2 = y + self.height
        c = (90,20,65,255)
        colorData = []
        numVertices = 4
        for i in range(numVertices * len(c)):
            i2 = i % numVertices
            colorData.append(c[i2])
        

        self.layout.x = x
        self.layout.y = y
        self.layout.width = width
        self.layout.height = height
        self.doc.set_style(0,0,dict(font_name='Arial', font_size=12))
        if self.bgRect is not None:
            self.bgRect.delete()
        self.bgRect = self.batch.add(4, GL_QUADS, mgGroup,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', colorData))
        self.titleLabel.x = x + 10
        self.titleLabel.y = y + 10

        
    def _resetDoc(self):
        text = ""
        first = True
        for item in self.msgs:
            attStr = item.string + '\n'
            if first:
                first = False
                attStr = "{bold True}" + item.string + "{bold False}\n"
            text += attStr + "\n"
        self.layout.document = pyglet.text.decode_attributed(text)
        
        
    def removeLine(self, item):
        print "remove"
        before = self.doc.text[:item.index]
        endIndex = item.index + len(item)
        after = self.doc.text[endIndex:]
        print "before: " + str(item.index)
        print "after: " + str(endIndex)
        self.doc.text = before + after
        msgsN = self.msgs
        #msgsN.remove(item.num)
        for msg in msgsN:
            msg.num -= 1
            msg.index -= len(item)
            print msg.num,msg.index
    
    def insertStart(self, item):
        print item.index, len(item)
        self.doc.text = item.string + "\n" + self.doc.text
        self.numMsgs += 1
        for msg in self.msgs[1:]:
            msg.index += len(item) + 1
            msg.num += 1
    
    def addMessage(self, msg):
        if len(self.msgs) and msg == self.msgs[0].string:
            return
        #print self.currentPos
        item = Message(self.numMsgs, msg, floor(self.secs), 0)
        self.msgs.insert(0,item)
        #self.insertStart(item)
        if self.layout.content_height >= self.height - self.titleLabel.content_height - 5:
            self.msgs = self.msgs[:len(self.msgs)-1]
            #self.removeLine(msg.index)
        self.currentPos = len(self.doc.text)
        self._resetDoc()
            
    def update(self, dt):
        self.dt += dt
        secs = floor(self.dt)
        if secs != self.secs and len(self.msgs):
            # only check for expiries once a second
            self.secs = secs
            toRemove = []
            for item in self.msgs:
                if item.isExpired(secs):
                    toRemove.append(item)
            if len(toRemove) > 0:
                for item in toRemove:
                    self.msgs.remove(item)
                    #self.removeLine(item)
                self._resetDoc()
                
class DemandIndicatorWidget(object):
    def __init__(self):
        pass

class Widget(object):
    def __init__(self):
        pass
    
    def layout(self):
        pass

'''self.dateLabel.text = "Jan 1900"
self.dateLabel.x = self.x + self.width - self.border\
                - self.dateLabel.content_width
self.dateLabel.y = self.y + 220 + 4 + self.fundsLabel.content_height * 2
self.populationLabel.text = "Population: 0"
self.populationLabel.x = self.x + self.width - self.border\
                - self.populationLabel.content_width'''

class InfoPane(object):
    def __init__(self, engine, x, y, width, height):
        self.engine = engine
        self.border = 10
        self.batch = pyglet.graphics.Batch()

        self.msgs = MessageQueue(self.batch, width - 20)
        self.fundsLabel = Label(batch=self.batch,
                                group=fgGroup)
        self.dateLabel = Label(batch=self.batch,
                                group=fgGroup)
        self.populationLabel = Label(batch=self.batch,
                                     group=fgGroup)
        self.resize(x,y,width,height)
        
        self.reset(engine)
        
    def reset(self, engine):
        self.engine = engine
        engine.push_handlers(self)
        self.on_funds_changed()
        self.on_census_changed()
        
    def resize(self, x, y, width, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = 300
        self.createBackground()
        self.msgs.doLayout(self.x + self.border, self.border, 
                         280, 200)
        #self.y + 220
        
        

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
        
    def city_message(self, msg):
        self.msgs.addMessage(msg)
        
    def on_census_changed(self):
        self.dateLabel.text = "Jan 1900"
        self.populationLabel.text = "Population: 0"
        self.dateLabel.x = self.x + self.width - self.border\
                                - self.dateLabel.content_width
        self.dateLabel.y = self.fundsLabel.y + self.fundsLabel.content_height + 2
        self.populationLabel.x = self.x + self.width - self.border\
                                - self.populationLabel.content_width
        self.populationLabel.y = self.y + 220
        
    def on_funds_changed(self):
        self.fundsLabel.text = "Treasury: $" + str(self.engine.budget.funds)
        # right-align label, respecting border
        self.fundsLabel.x = self.x + self.width - self.border\
                                - self.fundsLabel.content_width
        self.fundsLabel.y = self.y + 220 + 2 + self.fundsLabel.content_height
    
    def update(self, dt):
        self.msgs.update(dt)
        self.updateDateLabel()
    
    def formatGameDate(self, cityTime):
        y = 1900 + cityTime / 48
        m = (cityTime % 48) / 4
        #d = "Week " + str((cityTime % 4) + 1)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        m = months[m-1]
        return "{} {}".format(m,y)
        
        
    def updateDateLabel(self):
        self.dateLabel.text = self.formatGameDate(self.engine.cityTime)
        self.dateLabel.x = self.x + self.width - self.border\
                                - self.dateLabel.content_width
        # update population
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    