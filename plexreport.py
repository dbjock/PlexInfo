import sys
import getpass
import logging
import traceback
# app specific modules
from plexapi.myplex import MyPlexAccount
import plexinfo.plexutils as myutil

if __name__ == '__main__':
    #####################
    # Simple command line parse
    if len(sys.argv) < 2:
        print(f"Must provide a the name of the Plex server you are wanting to connnect to")
        sys.exit(1)

    svrName = sys.argv[1]

    userName = "dbjock"
    userPass = getpass.getpass(prompt=f"Enter {userName}'s Plex Password: ")
    print(f"Authenticating {userName}", end=" : ")
    account = MyPlexAccount(userName, userPass)
    # TODO: Better handling of an login error.
    print("Authenticated")
    print("That is all I can do at this time")
