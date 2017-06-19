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

If you want to run it again, you have to call `make stop` first in order to stop the running container, and then call the `all` directive :

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

* crawl one or many Jahia zip file
* unzip it
* parse it
* export its content
* run a nginx docker image to serve the exported content

The detailed commands look like this :

```
python src/jahiap.py crawl dcsl -o build
python src/jahiap.py unzip dcsl -o build
python src/jahiap.py parse dcsl -o build -r
python src/jahiap.py export dcsl -o build -s
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
$ python src/jahiap.py  -h
Usage:
  jahiap.py crawl <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--date DATE] [--force] [--debug|--quiet]
  jahiap.py unzip <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--date DATE] [--force] [--debug|--quiet]
  jahiap.py parse <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--print-report] [--date DATE] [--force]
                         [--debug|--quiet]
  jahiap.py export <site> [--to-wordpress|--to-static|--to-dictionary|--clean-wordpress] [--output-dir=<OUTPUT_DIR>]
                          [--number=<NUMBER>] [--site-url=<SITE_URL>] [--print-report] [--date DATE] [--force]
                          [--debug|--quiet]

Options:
  -h --help                     Show this screen.
  -v --version                  Show version.
  -o --output-dir=<OUTPUT_DIR>  Directory where to perform command [default: build].
  -n --number=<NUMBER>          Number of sites to analyse (fetched in JAHIA_SITES, from given site name) [default: 1].
  --date DATE                   Date and time for the snapshot, e.g : 2017-01-15-23-00.
  -f --force                    Force download even if existing files for same site.
  -r --print-report             Print report with content.
  -w --to-wordpress             Export parsed data to Wordpress.
  -c --clean-wordpress          Delete all content of Wordpress site.
  -s --to-static                Export parsed data to static HTML files.
  -d --to-dictionary            Export parsed data to python dictionary.
  -u --site-url=<SITE_URL>      Wordpress URL where to export parsed content.
  --debug                       Set logging level to DEBUG (default is INFO).
  --quiet                       Set logging level to WARNING (default is INFO).
```

The command relies on the following environment variables :

```
export JAHIA_HOST="localhost"
export JAHIA_ROOT_USER='root'
export JAHIA_ROOT_PASSWORD=xxx
```
The third one is mandatory, i.e the script will not run if it is not set. For the two first ones, the values above are used by default.

Quick example to download dcsl zip:

```
python src/jahiap.py crawl dcsl -o build
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
