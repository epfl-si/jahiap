A Jahia parser that takes the export of a Jahia site
and transforms it into something else (e.g. a static
site).

## Install

pip install -r requirements/base.txt

## The 30-seconds tutorial (for dcsl)

```
$ cd jahiap
$ make all
```

You now can access the content at [http://localhost:9090](http://localhost:9090).

Again ?

```
$ make stop all
```

For another website, e.g master?

```
$ make all port=9091 site_name=master zip_file=exports/master_export_2017-05-29-10-53.zip
```
This one will be available at [http://localhost:9091](http://localhost:9091).

## More details on usage

The `make` command does a few things for you :

* unzip a Jahia file
* parse it
* export its content
* run a nginx docker image to serve the exported content

The detailed commands look like this :

```
python jahiap.py -o build unzip exports/dcsl_export_2017-05-30-09-44.zip
python jahiap.py -o build parse dcsl -r
python jahiap.py -o build export dcsl -s
docker run -d \
    --name docker-dcsl \
    -p 9090:80 \
    -v $(PWD)/build/dcsl_html:/usr/share/nginx/html \
    nginx
```

## nginx

the `make` command starts docker nginx with optionals parameters site_name=dcsl, port=xxx (default=9090), docker_name=xxx (default=demo-dcsl) and static files from $(PWD)/$(output_dir)/$(site_name)_html (default=./build/dcsl_html)

```
make start
make start site_name=dcsl port=9090 docker_name=demo-dcsl output_dir=build
```

stop and remove nginx container

```
make stop
make stop docker_name=demo-dcsl
```

stop and restart nginx

```
make restart
```

## jahiap

You might use the option `-h` on the jahiap script to get the following help:

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
usage: jahiap.py unzip [-h] zip_file

positional arguments:
  zip_file    path to Jahia zip file

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
  -w, --to-wordpress    export parsed data to WordPress
  -s, --to-static       export parsed data to static HTML files
  -u URL, --site-url URL
                        WordPress URL where to export parsed content
```

## Downloading zip files

The script `crawl.py` is provided to download the Jahia zip files. It relies on the following environment variables :

```
export JAHIA_HOST="localhost"
export JAHIA_ROOT_USER='root'
export JAHIA_ROOT_PASSWORD=xxx
```
The third one is mandatory, i.e the script will not run if it is not set. For the two first ones, the values above are used by default.

Quick example to download dcsl zip:

```
python crawl.py dcsl
```

More options are available to change the output directory, the date of the snapshot or the level of logs. Use option `-h` to get the following help :

```
usage: crawl.py [-h] [--debug] [--quiet] [-o OUTPUT] [-d DATE] SITE

Crawl Jahia zip files

positional arguments:
  SITE                  site name (in jahia admin) of site to get the zip for

optional arguments:
  -h, --help            show this help message and exit
  --debug               Set logging level to DEBUG (default is INFO)
  --quiet               Set logging level to WARNING (default is INFO)
  -o OUTPUT, --output OUTPUT
                        path where to download files
  -d DATE, --date DATE  date and time for the snapshot, e.g : 2017-01-15-23-00
```

## Testing

The testing tool [pytest](https://docs.pytest.org/en/latest/contents.html) comes with the requirements. You can run the full suite with :

```
$ pytest
```

Or you migth run a specific file or class or test with

```
$ pytest test/test_parser.py
$ pytest test/test_parser.py::TestSiteProperties
$ pytest test/test_parser.py::TestSiteProperties::test_name
...
```

Or you might choose to target some of those specific areas:

* TestSiteProperties
* TestSiteStructure
* TestSidebar
* TestHomepage


```
$ pytest -k TestSiteStructure
```
