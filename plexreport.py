import sys
import getpass
import logging.config
import yaml
from pathlib import Path

# app specific modules
from plexinfo import sqlitedb as mydb
from plexinfo import plexutils as myutil
from plexapi.myplex import MyPlexAccount

logger = logging.getLogger("PlexReport")

with open("log.conf", 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)


def main():
    userName = "dbjock"
    #####################
    # Simple command line parse
    if len(sys.argv) < 2:
        print(f"Must provide a the name of the Plex server you are wanting to connnect to")
        sys.exit(1)

    svrName = sys.argv[1]
    plexRptData = Path.cwd() / 'Data'
    plexScripts = Path.cwd() / 'Scripts'

    logger.debug(f"getpass from user {userName}")
    userPass = getpass.getpass(prompt=f"Enter {userName}'s Plex Password: ")
    print(f"Authenticating {userName}")
    logger.info(f"Authenticating {userName} to plex server {svrName}")
    try:
        account = MyPlexAccount(userName, userPass)
    except Exception as err:
        logger.critical(f"Error:  {err}", exc_info=True)
        sys.exit()

    logger.debug(f"username: {userName} authenticated.")
    print("Authenticated")
    print("That is all I can do at this time")


if __name__ == '__main__':
    main()
