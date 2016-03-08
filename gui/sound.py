import os
import ConfigParser

import pyglet
from pyglet.media import Player

import gui

import logging
logger = logging.getLogger(__name__)


class SoundPlayer(object):
    def __init__(self, soundDirPath):
        self.soundDirPath = soundDirPath
        self.loadSounds()
        self.musicPlayer = Player()
        self.queue = False
        self.queuePlayer = None
        self.enabled = True
        self.soundEffectVolume = 1.0  # between 0.0 and 1.0
        self._musicVolume = 1.0  # between 0.0 and 1.0

    '''
        loads sounds from gui config file into dict.
        maps name to pyglet sound object.
        if ',stream' exists after filename in config file,
         will stream file instead of loading the whole thing in once.
    '''
    def loadSounds(self):
        self.sounds = dict()
        soundTypes = dict(gui.config.items('sound_events'))
        for key in soundTypes:
            self._loadSoundResource(key)

    @staticmethod
    def _loadSoundEntry(key):
        entry = gui.config.get('sound_events', key)
        if ',' in entry:
            sp = entry.split(",")
            fileName = sp[0]
            if sp[1] == "stream":
                stream = True
        else:
            fileName = entry
            stream = False
        return fileName, stream

    def _loadSoundResource(self, key):
        fileName, stream = self._loadSoundEntry(key)
        if key in self.sounds:
            self.sounds[key].delete()
        self.sounds[key] = pyglet.resource.media(self.soundDirPath + fileName, streaming=stream)

    def shutdown(self):
        from pyglet.media import avbin
        if self.musicPlayer.source is not None:
            avbin.av.avbin_close_file(self.musicPlayer.source._file)  # hack to ensure avbin closes properly.
        self.musicPlayer.delete()
        toDel = self.sounds.keys()
        for snd in toDel:
            del self.sounds[snd]

    @property
    def musicVolume(self):
        return self._soundEffectVolume

    @musicVolume.setter
    def musicVolume(self, value):
        self.musicPlayer.volume = value
        self._musicVolume = self.musicPlayer.volume

    def setMute(self, value):
        self.enabled = value

    def getSound(self, soundName):
        try:
            snd = self.sounds[soundName.lower()]
        except KeyError:
            print "Sound requsted to be played does not exist in config file."
            return None
        return snd

    def playMusic(self, soundName):
        if not self.enabled:
            return
        soundName = soundName.lower()
        snd = self.getSound(soundName)
        assert snd
        if self.musicPlayer.playing and self.musicPlayer.source == snd:
            self.musicPlayer.seek(0)
            return
        else:
            # reload sound and reset Player obj
            # (streaming sounds needs to be reloaded every time)
            if isinstance(snd, pyglet.media.StreamingSource):
                self._loadSoundResource(soundName)
            self.musicPlayer.delete()
            self.musicPlayer = Player()
            self.musicPlayer.volume = self._musicVolume
        looper = pyglet.media.SourceGroup(snd.audio_format, None)
        looper.loop = True
        looper.queue(snd)
        self.musicPlayer.queue(looper)
        self.musicPlayer.play()

    def playEffect(self, soundName):
        if not self.enabled:
            return
        soundName = soundName.lower()
        snd = self.getSound(soundName)
        assert snd
        p = Player()
        p.volume = self.soundEffectVolume
        p.queue(snd)
        p.play()

    def startEffectsQueue(self):
        self.queue = True
        self.queuePlayer = Player()

    def queueEffect(self, soundName):
        if not self.enabled:
            return
        soundName = soundName.lower()
        snd = self.getSound(soundName)
        assert snd
        self.queuePlayer.queue(snd)

    '''
        Plays the queue and resets queue state.
    '''
    def playEffectsQueue(self):
        self.queuePlayer.volume = self.soundEffectVolume
        self.queuePlayer.play()
        self.queue = False
        self.queuePlayer = None
