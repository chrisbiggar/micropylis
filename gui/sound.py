import pyglet
from pyglet.media import Player

class Sound(object):
    def __init__(self, name, file, stream=False):
        self.name = name
        self.file = file
        self.stream = stream

sounds = [
    Sound('music', 'res/sound/music.mp3', True)
]

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
        self.player.queue(self.sounds[sound])
        self.player.play()