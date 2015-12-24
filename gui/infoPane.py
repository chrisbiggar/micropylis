'''
Created on Oct 29, 2015

@author: chris
'''
from math import floor
import pyglet
from pyglet.text import Label
from pyglet.text.layout import TextLayout
from pyglet.text.document import UnformattedDocument, FormattedDocument
from pyglet.gl import *
from layoutManager import Widget,Frame,LayoutLabel,VerticalLayout


bgGroup = pyglet.graphics.OrderedGroup(1)
mgGroup = pyglet.graphics.OrderedGroup(2)
fgGroup = pyglet.graphics.OrderedGroup(3)

MSG_SHOW_TIME = 8 # in seconds
MSG_DELETE_FREQ = 0.5


class Message(object):
    def __init__(self, num, msg, startTime, start):
        self.string = msg
        self.time = int(startTime)
        self.index = start
        self.num = num
    
    def isExpired(self, secs):
        return int(secs) > self.time + MSG_SHOW_TIME * 2
    
    def __len__(self):
        return len(self.string)
    

'''
    displays messages to user. 
'''
class MessageQueue(Widget):
    def __init__(self, batch):
        super(MessageQueue,self).__init__()
        
        self.titleLabel = None
        self.textLayout = None
        self.batch = batch
        self.msgs = list()
        self.dt = 0
        self.halfSecs = 0
        self.bgRect = None
        self.doc = FormattedDocument()

        self.currentPos = 0
        self.numMsgs = 0
    
    def delete(self):
        if self.textLayout is not None:
            self.textLayout.delete()
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
    
    def size(self, window):
        super(MessageQueue,self).size(window)
        
        if self.textLayout is not None:
            self.textLayout.delete()
        if self.titleLabel is not None:
            self.titleLabel.delete()
        
        self.width = window.width or 200
        self.height = 200
        
        if self.textLayout is None:
            self.textLayout = TextLayout(self.doc,
                                         width=self.width,
                                         batch=self.batch,
                                         group=fgGroup,
                                         multiline=True)
        else:
            self.textLayout.width = self.width
        
        if self.titleLabel is None:
            self.titleLabel = Label("City Messages",
                                    x=self.x+10,y=self.y+10,
                                    batch=self.batch,
                                    group=fgGroup)
        else:
            self.titleLabel.x = self.x + 10
            self.titleLabel.y = self.y + 10
        self.createBackground()

        
    def createBackground(self):
        x = self.x
        y = self.y
        x2 = x + self.width
        y2 = y + self.height
        c = (38, 89, 106, 255)
        colorData = []
        numVertices = 4
        for i in xrange(numVertices * len(c)):
            i2 = i % numVertices
            colorData.append(c[i2])
        
        self.textLayout.x = x
        self.textLayout.y = y
        self.textLayout.width = self.width
        self.textLayout.height = self.height
        self.doc.set_style(0,0,dict(font_name='Arial', font_size=12))
        if self.bgRect is not None:
            self.bgRect.delete()
            self.bgRect = None
        self.bgRect = self.batch.add(4, GL_QUADS, mgGroup,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', colorData))
        
        
        
    def deleteMsg(self, item):
        self.msgs.remove(item)
        self.doc.delete_text(item.index, item.index + len(item))
        for msg in self.msgs:
            if msg.num > item.num:
                msg.num -= 1
                msg.index -= len(item)
        
    
    def addMessage(self, message):
        if len(self.msgs) and message == self.msgs[0].string:
            return
        
        message = message + '\n'
        item = Message(0, message, self.halfSecs, 0)
        
        self.doc.set_style(0, len(self.doc.text), {'bold' : False})
        for msg in self.msgs:
            msg.num += 1
            msg.index += len(item)
        
        self.msgs.insert(0,item)
        self.doc.insert_text(0, message, {'bold' : True})
        
        if self.textLayout is not None:
            while self.textLayout.content_height >= self.height - self.titleLabel.content_height:
                item = self.msgs[len(self.msgs)-1]
                self.deleteMsg(item)
        
            
    def update(self, dt):
        self.dt += dt
        if self.dt >= MSG_DELETE_FREQ:
            # expired messages are collected on 0.5 sec freq
            self.halfSecs += 1
            self.dt = self.dt % MSG_DELETE_FREQ
            toRemove = []
            for item in self.msgs:
                if item.isExpired(self.halfSecs):
                    toRemove.append(item)
            if len(toRemove):
                for item in toRemove:
                    self.deleteMsg(item)


class DemandIndicatorWidget(object):
    def __init__(self):
        pass


class InfoPane(Frame):
    WIDTH = 300
    def __init__(self, engine):
        self.months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        self.batch = pyglet.graphics.Batch()
        self.engine = engine
        self.border = 10
        
        self.fgGroup = fgGroup
        
        self.bg = None
        
        self.fundsLabel = LayoutLabel(self)
        self.dateLabel = LayoutLabel(self)
        self.populationLabel = LayoutLabel(self)
        self.msgs = MessageQueue(self.batch)
        
        super(InfoPane,self).__init__(
                            VerticalLayout([self.dateLabel,
                                            self.fundsLabel,
                                            self.populationLabel,
                                            self.msgs]))
        
        
        self.reset(engine)
        self.updateDateLabel()
        self.alive = False

           
    def reset(self, engine):
        self.engine = engine
        engine.push_handlers(self)
        self.lastTime = self.engine.cityTime
        self.on_funds_changed()
        self.on_census_changed()
        self.resetBackground()
        self.setNeedsLayout()
        
    def delete(self):
        if self.bg is not None:
            self.bg.delete()
            self.bg = None
        self.content.delete()
        
    
    def size(self,window):
        super(InfoPane,self).size(window)
        #print window.width
        if window.width < 800:
            self.delete()
            self.width = self.height = 1
        self.alive = True
        self.resetBackground()
        #print "reset background"

    def resetBackground(self):
        if self.bg is not None:
            self.bg.delete()
            self.bg = None
        x = self.x
        y = self.y
        x2 = self.x + self.width
        y2 = self.x + self.height
        c = (22, 33, 85, 255)
        self.bg = self.batch.add(4, GL_QUADS, bgGroup,
                                 ('v2f', [x, y, x2, y, x2, y2, x, y2]),
                                 ('c4B', [c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]
                                    ,c[0],c[1],c[2],c[3],c[0],c[1],c[2],c[3]]))
        
    
    def addInfoMessage(self, msg):
        self.msgs.addMessage(msg)


    def city_message(self, msg):
        self.msgs.addMessage(msg)


    def on_census_changed(self):
        self.populationLabel.set_text("Population: 0")

     
    def on_funds_changed(self):
        self.fundsLabel.set_text("Treasury: $" + str(self.engine.budget.funds))
        
    
    def update(self, dt):
        self.msgs.update(dt)
        if (self.lastTime != self.engine.cityTime and
                self.lastTime + 4 <= self.engine.cityTime):
            self.lastTime = self.engine.cityTime
            self.updateDateLabel()
            
    
    def formatGameDate(self, cityTime):
        year = 1900 + cityTime / 48
        month = self.months[(cityTime % 48) / 4]
        #d = "Week " + str((cityTime % 4) + 1)
        return "{} {}".format(month,year)
        
        
    def updateDateLabel(self):
        #print "update date label"
        d = self.formatGameDate(self.engine.cityTime)
        self.dateLabel.set_text(d)
        # update population
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    