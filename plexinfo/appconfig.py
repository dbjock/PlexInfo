# Module to read/set application configuration file
from configparser import ConfigParser

# sec_main is the [main] section of the config file.
sec_main = dict()


def loadCfg(cfgFile):
    cfgParser = ConfigParser()
    cfgParser.read(cfgFile)

    for k, v in cfgParser.items('main'):
        sec_main[k] = v
