import os
import ConfigParser

import pyglet
from pyglet.media import Player

import gui

class Sound(object):
    def __init__(self, name, file, stream=False):
        self.name = name
        self.file = file
        self.stream = stream

sounds = []
soundNames = []
searchPath = "res/sound/"
for f in os.listdir(searchPath):
    name = os.path.splitext(f)
    sounds.append(Sound(name[0], searchPath + f))
    soundNames.append(name[0])

assert len(soundNames) == len(set(soundNames)),\
        "Duplicate Sound File Names. There are two files with same base name excluding extension."


class Sounds(object):
    def __init__(self):
        self.player = Player()
        self.sounds = dict()
        self.loadSounds(sounds)

    def setEnabled(self, value):
        if value:
            self.player.volume = 1.0
        else:
            self.player.volume = 0.0

    def loadSounds(self, sounds):
        for sound in sounds:
            self.sounds[sound.name] = pyglet.media.load(sound.file, streaming=sound.stream)

    def playSound(self, sound):
        try:
            key = gui.config.get("sounds", sound)
        except ConfigParser.NoOptionError:
            print "Sound requsted to be played does not exist in config file."
            return
        self.player.queue(self.sounds[key])
        self.player.play()