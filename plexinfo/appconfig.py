# Module to read/set application configuration file
from configparser import ConfigParser

# sec_main is the [main] section of the config file.
sec_compare = dict()
sec_db = dict()


def loadCfg(cfgFile):
    cfgParser = ConfigParser()
    cfgParser.read(cfgFile)

    for k, v in cfgParser.items('compare'):
        sec_compare[k] = v

    for k, v in cfgParser.items('db'):
        sec_db[k] = v
