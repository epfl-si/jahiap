A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

pip install -r requirements/base.txt

## Usage

The script might be used for different actions: unzipping an Jahia file, parsing it, or exporting its content. Here is a 10-seconds example, which

* makes use of a JAHIA zip file in `exports/dcsl_export_2017-05-30-09-44.zip`
* works in the `build` sub-directory

```
python jahiap.py -o build unzip exports/dcsl_export_2017-05-30-09-44.zip
python jahiap.py -o build parse dcsl -r
python jahiap.py -o build export dcsl -s
```

You might use the option `-h` to get the following help:

```
$ python jahiap.py  -h
usage: jahiap.py [-h] [--debug] [--quiet] [-o OUTPUT_DIR]
                 {unzip,parse,export} ...

Unzip, parse and export Jahia XML

positional arguments:
  {unzip,parse,export}

optional arguments:
  -h, --help            show this help message and exit
  --debug               Set logging level to DEBUG (default is INFO)
  --quiet               Set logging level to WARNING (default is INFO)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        directory where to unzip, parse, export Jahia XML
```

More help on each command can be displayed with the command name followed by `-h`. See next section for more details.

### Unzip

```
$ python jahiap.py unzip -h
usage: jahiap.py unzip [-h] xml_file

positional arguments:
  xml_file    path to Jahia XML file

optional arguments:
  -h, --help  show this help message and exit
```

### Parse

```
$ python jahiap.py parse -h
usage: jahiap.py parse [-h] [-r] site_name

positional arguments:
  site_name           name of sub directories that contain the site files

optional arguments:
  -h, --help          show this help message and exit
  -r, --print-report  print report with parsed content
```

### Export

```
$ python jahiap.py export -h
usage: jahiap.py export [-h] [-w] [-s] [-u URL] site_name

positional arguments:
  site_name             name of sub directories that contain the site files

optional arguments:
  -h, --help            show this help message and exit
  -w, --to-wordpress    export parsed data to Wordpress
  -s, --to-static       export parsed data to static HTML files
  -u URL, --site-url URL
                        wordpress URL where to export parsed content
```

## Testing

The testing tool [pytest](https://docs.pytest.org/en/latest/contents.html) comes with the requirements. You can run the full suite with :

```
$ pytest
...
```

Or you might choose to target some of those specific areas:

* TestSiteProperties
* TestSiteStructure
* TestSidebar
* TestHomepage


```
$ pytest -k TestSiteStructure
...
```


### How to start a static site nginx ? ###

start docker nginx with optinals paratemers port=xxx and name=xxx
default port=9090 
name=demo-static

```
make start
make start port=9090 name=demo-static
```

stop and remove nginix container

```
make stop
make stop name=demo-static
```

stop and restart nginix

```
make restart
make restart name=demo-static port=9090
```