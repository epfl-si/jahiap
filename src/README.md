A Jahia parser that takes the export of a Jahia site and transforms it into
something else (e.g. a static site).

## jahiap.py

You might use the option `-h` on the jahiap script to get the following help:

```
$ python src/jahiap.py  -h
Usage:
  jahiap.py crawl <site>  [--output-dir=<OUTPUT_DIR>] [--export-path=<EXPORT_PATH>]
                          [--number=<NUMBER>] [--date DATE] [--force] [--debug | --quiet]
  jahiap.py unzip <site>  [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug | --quiet]
  jahiap.py parse <site>  [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--print-report]
                          [--debug | --quiet] [--use-cache] [--site-path=<SITE_PATH>]
  jahiap.py export <site> [--clean-wordpress | --to-wordpress | --nginx-conf]
                          [--wp-cli=<WP_CLI> --site-host=<SITE_HOST> --site-path=<SITE_PATH>]
                          [--to-static --to-dictionary --number=<NUMBER> --print-report]
                          [--output-dir=<OUTPUT_DIR> --export-path=<EXPORT_PATH>]
                          [--use-cache] [--debug | --quiet]
  jahiap.py docker <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug | --quiet]
  jahiap.py generate [--output-dir=<OUTPUT_DIR>] [--debug | --quiet]

Options:
  -h --help                     Show this screen.
  -v --version                  Show version.
  -o --output-dir=<OUTPUT_DIR>  Directory where to perform command [default: build].
  -n --number=<NUMBER>          Number of sites to analyse (fetched in JAHIA_SITES, from given site name) [default: 1].
  --export-path=<EXPORT_PATH>   (crawl) Directory where Jahia Zip files are stored
  --date DATE                   (crawl) Date and time for the snapshot, e.g : 2017-01-15-23-00.
  -f --force                    (crawl) Force download even if existing snapshot for same site.
  --use-cache                   (parse) Do not parse if pickle file found with a previous parsing result
  --site-path=<SITE_PATH>       (parse, export) sub dir where to export parsed content. (default is '' or $WP_PATH on command 'docker')
  -r --print-report             (FIXME) Print report with content.
  --nginx-conf                  (export) Only export pages to WordPress in order to generate nginx conf
  -s --to-static                (export) Export parsed data to static HTML files.
  -d --to-dictionary            (export) Export parsed data to python dictionary.
  -c --clean-wordpress          (export) Delete all content of WordPress site.
  -w --to-wordpress             (export) Export parsed data to WordPress and generate nginx conf
  --wp-cli=<WP_CLI>             (export) Name of wp-cli container to use with given WordPress URL. (default WPExporter)
  --site-host=<SITE_HOST>       (export) WordPress HOST where to export parsed content. (default is $WP_ADMIN_URL)
  --debug                       (*) Set logging level to DEBUG (default is INFO).
  --quiet                       (*) Set logging level to WARNING (default is INFO).
```

Quick example to download dcsl zip:

```
python src/jahiap.py crawl dcsl
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
