import os, sys, logging
import pyglet
from util.config import Config

global config
global cityMessages
config = Config()
config.readfp(pyglet.resource.file('res/gui.cfg'))
cityMessages = Config()
cityMessages.readfp(pyglet.resource.file('res/citymessages.cfg'))

BG_RENDER_ORDER = 1
MG_RENDER_ORDER = 2
FG_RENDER_ORDER = 3

GUI_PANEL_RENDER_ORDER = 20
GUI_BG_RENDER_ORDER = 24
GUI_FG_RENDER_ORDER = 28
GUI_HIGHLIGHT_RENDER_ORDER = 32

global tempDir
tempDir = None
