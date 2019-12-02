# support-tools

Few scripts for creating/converting modules for Encounter+ iOS app

## Usage

```
usage: convert.py [-h] [--parser PARSER] [--debug] [--name NAME]
                  [--author AUTHOR] [--cover COVER] [--code CODE] [--id ID]
                  PATH

Convert existing modules to Encounter+ compatible file

positional arguments:
  PATH             a path to .mod, .xml, .db3 file to convert

optional arguments:
  -h, --help       show this help message and exit
  --parser PARSER  data parser (fg|beyond)
  --debug          enable debug logs
  --name NAME      name
  --author AUTHOR  author
  --cover COVER    cover image
  --code CODE      short code
  --id ID          id
  ```

## Example

```
./convert.py ~/test.mod --name "Test Module"
```

## Dependencies

```
natsort, slugify
```

## Python3 install

```
pip3 install natsort
pip3 install python-slugify
```

## Known issues

`unpack_archive` is not working properly with python2.7, but it should be working with python3

