import ConfigParser


class Config(ConfigParser.ConfigParser):
    '''def __init__(self, defaultsFile):
        super(ConfigParser, self).__init__(defaultsFile)'''

    def getFloat(self, section, option):
        return float(self.get(section, option))

    def getInt(self, section, option):
        return int(self.get(section, option))