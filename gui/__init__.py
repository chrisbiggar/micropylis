

import ConfigParser

global config
global cityMessages

config = ConfigParser.ConfigParser()
config.read('res/gui.cfg')

cityMessages = ConfigParser.ConfigParser()
cityMessages.read('res/citymessages.cfg')

