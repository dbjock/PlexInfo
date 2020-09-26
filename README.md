Table of contents
- [Plexcompare](#plexcompare)
  - [Requirements](#requirements)
  - [Change Log](#change-log)
  - [Usage](#usage)
  - [Configuration](#configuration)
    - [Section [compare]](#section-compare)
    - [Section [db]](#section-db)
  - [Commands](#commands)
    - [movie](#movie)
# Plexcompare
Tool to compare libraries and collections from one plex server to another, and reporting the differences. Especially helpful when moving a plex server from a Windows to a Linux/MacOS since drive letters do not exist on one OS.

The application will not make any changes to data Plex. It will create csv files, that excel, or any tool of your choice, can be used to extract the info you wish.

## Requirements
Tested with python 3.6.8 on windows
- PlexAPI
- YAML

## Change Log
| Version  | Notes |
| ------------- | ------------- |
| .1| Initial release|


## Usage
```
usage: plexreport.py [-h] -u plex_userid {movie} ...

optional arguments:
  -h, --help      show this help message and exit
  -u plex_userid  The Plex User ID

Commands:
  {movie}
    movie         Get a comparison report for a movie library including it's
                  collections
```
## Configuration
The Plexcompare application will work fine with out a configuration file, however there are settings which you may want to use to further control plexcompare. The configuration file uses the INI file format. All configuration variables and sections in the file are optional.

The configuration file location is set with the environment variable PLEXCOMPARE_CONFIG_FILE


### Section [compare]
This section is specific for settings to the plexcompare application. As stated before this section is optional, and all settings are optional.

**collectionmax**

Maximum number of collection objects that will be loaded for a movie library. Let's say you were testing with a movie library which has a large number of collections. This can limit the number of collections that will be loaded and compared instead of waiting for all to be loaded.

Example below will limit the loading of only 5 movies l
```
[compare]
collectionmax=5
```

**moviemax**

Maximum number of video objects that will be loaded for a movie library. Example for using this is your testing are a very large movie library and want to limit the number of movies it will load. Set this to a number larger than 0 will then limit the number of movie/video objects that will be loaded for comparing.

Example below will limit the loading of only 5 movies
```
[compare]
moviemax=5
```

### Section [db]
This section is specific for the datbase settings for all the plexinfo applications. As stated before this section is optional, and all settings are optional.

**filename**

By default the applications create the internal database in memory. This setting will override that and put the file on disk in the data directory local to the application.

Example below will create a file `myExample.db` in the `./data/` directory. Note, this is a sqlite3 database.
```
[db]
filename=myExample.db
```

## Commands
### movie
This is use to collect the movie and collection's from a specific movie library.
In order for this to work, make sure the directory path are the same for the movies. Thi sis to be sure the movie location can be parsed and be the same in order for comparisons to be reported accurately.

For example:
|Windows Path|Linux Path|
|-|-|
|`z:\MediaFolders\MyMovies\Movie A\ `| `/MediaFolders/MyMovies/Movie A/`
|`z:\MediaFolders\MyMovies\Movie B\ `| `/MediaFolders/MyMovies/Movie B/`

The example below would cause difference to all movies as there is nothing to identify as be the same.
|Windows Path|Linux Path|
|-|-|
|`z:\MediaFolders\MyMovies\Movie A\ `| `/MyMovies/Movie A/`
|`z:\MediaFolders\MyMovies\Movie B\ `| `/MyMovies/Movie B/`

```
usage: plexreport.py movie [-h] [--OutPath DirPath]
                           server_name server_name lib_name`

optional arguments:
  -h, --help         show this help message and exit

Comparison report for a Movie library including Collections:
  server_name        First plex server
  server_name        Second plex server
  lib_name           Movie library name
  --OutPath DirPath  Directory path where csv files will be placed. Default is
                     current directory`
```

*Example*

This will take movie library titled `NewReleases` and compare it's movies and collections on `UltraSrv1` and `OtherSrv`, using the plex account `BossMan`
```
python plexcompare.py -u BossMan --Movie NewReleases UltraSrv1 OtherSrv
```