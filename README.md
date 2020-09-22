Table of contents
- [Plexcompare](#plexcompare)
  - [Requirements](#requirements)
  - [Change Log](#change-log)
  - [Usage](#usage)
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