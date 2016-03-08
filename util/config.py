import ConfigParser


class Config(ConfigParser.ConfigParser):

    def getFloat(self, section, option):
        return float(self.get(section, option))

    def getInt(self, section, option):
        return int(self.get(section, option))