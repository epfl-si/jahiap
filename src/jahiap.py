"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017
jahiap: a wonderful tool

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
"""

import sys
import logging
import os
import pickle
import zipfile
import requests

from pprint import pprint, pformat
from datetime import datetime

from docopt import docopt

from exporter.html_exporter import HTMLExporter
from exporter.wp_exporter import WPExporter
from exporter.dict_exporter import DictExporter
from crawler import SiteCrawler
from jahia_site import Site

from settings import DOMAIN


def main(args):
    """
        Setup context (e.g debug level) and forward to command-dedicated main function
    """
    logging.info("Starting jahiap script...")

    # mkdir from output_dir or as temporary dir
    if args['--output-dir']:
        if not os.path.isdir(args['--output-dir']):
            os.makedirs(args['--output-dir'])
    else:
        raise SystemExit("Ouput '%s' does not exist. Please create it first" % args['--output-dir'])

    # Forward to appropriate main function
    call_command(args)


def call_command(args):
    """
    Forward to appropriate main function
    """
    for key, value in args.items():
        # filter options or arguments
        if key.startswith('-') or key.startswith('<'):
            continue
        # search command
        elif value:
            # call main_<command> method
            method_name = 'main_' + str(key)
            return getattr(sys.modules[__name__], method_name)(args)


def main_crawl(args):
    logging.info("starting crawling...")
    try:
        SiteCrawler.download(args)
    except requests.ConnectionError as err:
        logging.error(err)


def main_unzip(args):
    # get zip files according to args
    zip_files = SiteCrawler.download(args)

    # to store paths of downloaded zips
    unzipped_files = {}

    for site_name, zip_file in zip_files.items():

        # create subdir in output_dir
        output_subdir = os.path.join(args['--output-dir'], site_name)
        if output_subdir:
            if not os.path.isdir(output_subdir):
                os.mkdir(output_subdir)

        # check if unzipped files already exists
        unzip_path = os.path.join(output_subdir, site_name)
        if os.path.isdir(unzip_path):
            logging.info("Already unzipped %s" % unzip_path)
            unzipped_files[site_name] = unzip_path
            continue

        logging.info("Unzipping %s..." % zip_file)

        # make sure we have an input file
        if not zip_file or not os.path.isfile(zip_file):
            logging.error("Jahia zip file %s not found", zip_file)
            continue

        # create zipFile to manipulate / extract zip content
        export_zip = zipfile.ZipFile(zip_file, 'r')

        # make sure we have the zip containing the site
        zip_name = "%s.zip" % site_name
        if zip_name not in export_zip.namelist():
            logging.error("zip file %s not found in main zip" % zip_name)
            continue

        # extract the export zip file
        export_zip.extractall(output_subdir)
        export_zip.close()

        # unzip the zip with the files
        zip_path = os.path.join(output_subdir, zip_name)
        zip_ref_with_files = zipfile.ZipFile(zip_path, 'r')
        zip_ref_with_files.extractall(unzip_path)

        # log success
        logging.info("Site successfully extracted in %s" % unzip_path)
        unzipped_files[site_name] = unzip_path

    # return results
    return unzipped_files


def main_parse(args):
    # get list of sites to parse according to args
    site_dirs = main_unzip(args)

    # to store paths of parsed objects
    parsed_sites = {}

    for site_name, site_dir in site_dirs.items():
        # create subdir in output_dir
        output_subdir = os.path.join(args['--output-dir'], site_name)

        # check if already parsed
        pickle_file = os.path.join(output_subdir, 'parsed_%s.pkl' % site_name)
        # if os.path.exists(pickle_file):
        #     with open(pickle_file, 'rb') as input:
        #         logging.info("Loaded parsed site from %s" % pickle_file)
        #         parsed_sites[site_name] = pickle.load(input)
        #         continue

        logging.info("Parsing %s...", site_dir)
        site = Site(site_dir, site_name)

        print(site.report)

        # save parsed site on file system
        with open(pickle_file, 'wb') as output:
            pickle.dump(site, output, pickle.HIGHEST_PROTOCOL)

        # log success
        logging.info("Site successfully parsed, and saved into %s" % pickle_file)
        parsed_sites[site_name] = site

    # return results
    return parsed_sites


def main_export(args):
    # get list of parsed sites

    sites = main_parse(args)

    for site in sites.values():
        logging.info("Exporting %s ...", site.name)
        # create subdir in output_dir
        output_subdir = os.path.join(args['--output-dir'], site.name)

        if args['--clean-wordpress']:
            wp_exporter = WPExporter(site=site, domain=args['--site-url'])
            wp_exporter.delete_all_content()
            logging.info("Data of Wordpress site successfully deleted")

        if args['--to-wordpress']:
            wp_exporter = WPExporter(site=site, domain=args['--site-url'])
            wp_exporter.import_all_data_to_wordpress()
            logging.info("Site successfully exported to Wordpress")

        if args['--to-static']:
            export_path = os.path.join(output_subdir, "html")
            HTMLExporter(site, export_path)
            logging.info("Site successfully exported to HTML files")

        if args['--to-dictionary']:
            export_path = os.path.join(
                output_subdir, "%s_dict.py" % site.name)
            data = DictExporter.generate_data(site)
            pprint(data)
            with open(export_path, 'w') as output:
                output.write("%s_data = " % site.name)
                output.write(pformat(data))
                output.flush()
            logging.info("Site successfully exported to python dictionary")


def set_logging_config(args):
    """
    Set logging with the 'good' level
    """
    level = logging.INFO
    if args['--quiet']:
        level = logging.WARNING
    elif args['--debug']:
        level = logging.DEBUG
    logging.basicConfig(level=level)


def set_default_values(args):
    """
    Set default values of arguments 'args'
    The static default values are defined to the main docstring.
    The dynamic default values are defined in this method.
    """
    # Set default values
    if not args['--date']:
        args['--date'] = datetime.today().strftime("%Y-%m-%d-%H-%M")
    if not args['--site-url']:
        args['--site-url'] = DOMAIN
    return args


if __name__ == '__main__':

    # docopt return a dictionary with all arguments
    # __doc__ contains package docstring
    args = set_default_values(docopt(__doc__, version='0.1'))
    print(args)

    # set logging config before anything else
    set_logging_config(args)

    main(args)
