# Module to read/set application configuration file
from configparser import ConfigParser

# sec_main is the [main] section of the config file.
sec_compare = dict()
sec_db = dict()
sec_server = dict()


def loadCfg(cfgFile):
    cfgParser = ConfigParser()
    cfgParser.read(cfgFile)

    if cfgParser.has_section('server'):
        for k, v in cfgParser.items('server'):
            sec_server[k] = v

    if cfgParser.has_section('compare'):
        for k, v in cfgParser.items('compare'):
            sec_compare[k] = v

    if cfgParser.has_section('db'):
        for k, v in cfgParser.items('db'):
            sec_db[k] = v
