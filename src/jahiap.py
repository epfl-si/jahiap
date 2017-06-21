"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017
jahiap: a wonderful tool

Usage:
  jahiap.py generate
  jahiap.py crawl <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--date DATE] [--force] [--debug|--quiet]
  jahiap.py unzip <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug|--quiet]
  jahiap.py parse <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--print-report]
                         [--debug|--quiet] [--use-cache] [--root-path=<ROOT_PATH>]
  jahiap.py export <site> [--to-wordpress|--to-static|--to-dictionary|--clean-wordpress] [--output-dir=<OUTPUT_DIR>]
                          [--number=<NUMBER>] [--site-url=<SITE_URL>] [--print-report]
                          [--wp-cli=<WP_CLI>] [--debug|--quiet]
  jahiap.py docker <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug|--quiet]  

Options:
  -h --help                     Show this screen.
  -v --version                  Show version.
  -o --output-dir=<OUTPUT_DIR>  Directory where to perform command [default: build].
  -n --number=<NUMBER>          Number of sites to analyse (fetched in JAHIA_SITES, from given site name) [default: 1].
  --date DATE                   (crawl) Date and time for the snapshot, e.g : 2017-01-15-23-00.
  -f --force                    (crawl) Force download even if existing snapshot for same site.
  -c --use-cache                (parse) Do not parse if pickle file found with a previous parsing result
  --root-path=<ROOT_PATH>       (FIXME) Set base path for URLs (default is '' or $WP_PATH on command 'docker')
  -r --print-report             (FIXME) Print report with content.
  -w --to-wordpress             (export) Export parsed data to Wordpress.
  -c --clean-wordpress          (export) Delete all content of Wordpress site.
  -s --to-static                (export) Export parsed data to static HTML files.
  -d --to-dictionary            (export) Export parsed data to python dictionary.
  -u --site-url=<SITE_URL>      (export) Wordpress URL where to export parsed content. (default is $WP_ADMIN_URL)
  --wp-cli=<WP_CLI>             (export) Name of wp-cli container to use with given wordpress URL. (default is set by WPExporter)
  --debug                       (*) Set logging level to DEBUG (default is INFO).
  --quiet                       (*) Set logging level to WARNING (default is INFO).
"""
from generator.utils import Utils

VERSION = "0.2"

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

from settings import WP_ADMIN_URL, WP_HOST, WP_PATH


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

        # when using-cache: check if already parsed
        if args['--use-cache']:
            pickle_file = os.path.join(output_subdir, 'parsed_%s.pkl' % site_name)
            if os.path.exists(pickle_file):
                with open(pickle_file, 'rb') as input:
                    logging.info("Loaded parsed site from %s" % pickle_file)
                    parsed_sites[site_name] = pickle.load(input)
                    continue

        # FIXME : root-path should be given in exporter, not parser
        root_path = ""
        if args['--root-path']:
            root_path = "/%s/%s" % (args['--root-path'], site_name)
            logging.info("Parsing site for root_path %s", root_path)
        logging.info("Parsing %s...", site_dir)
        site = Site(site_dir, site_name, root_path=root_path)

        print(site.report)

        # when using-cache: save parsed site on file system
        if args['--use-cache']:
            with open(pickle_file, 'wb') as output:
                logging.info("Parsed site saved into %s" % pickle_file)
                pickle.dump(site, output, pickle.HIGHEST_PROTOCOL)

        # log success
        logging.info("Site successfully parsed")
        parsed_sites[site_name] = site

    # return results
    return parsed_sites


def main_export(args):
    # get list of parsed sites

    sites = main_parse(args)

    # to store results of exported parsed sites
    exported_sites = {}

    for site_name, site in sites.items():
        logging.info("Exporting %s ...", site.name)

        # store results
        exported_site = {}
        exported_sites[site_name] = exported_site

        # create subdir in output_dir
        output_subdir = os.path.join(args['--output-dir'], site.name)

        if args['--clean-wordpress']:
            wp_exporter = WPExporter(site=site, domain=args['--site-url'], cli_container=args['--wp-cli'])
            wp_exporter.delete_all_content()
            logging.info("Data of Wordpress site successfully deleted")

        if args['--to-wordpress']:
            wp_exporter = WPExporter(site=site, domain=args['--site-url'], cli_container=args['--wp-cli'])
            wp_exporter.import_all_data_to_wordpress()
            wp_exporter.generate_nginx_conf_file()
            exported_site['wordpress'] = args['--site-url']
            logging.info("Site successfully exported to Wordpress")

        if args['--to-static']:
            export_path = os.path.join(output_subdir, "html")
            HTMLExporter(site, export_path)
            exported_site['static'] = export_path
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
            exported_site['dict'] = export_path
            logging.info("Site successfully exported to python dictionary")

    # overall result : {site_name: {wordpress: URL, static: PATH, dict: PATH}, ...}
    return exported_sites

def main_docker(args):
    # get list of sites html static sites
    args['--to-static'] = True
    args['--root-path'] = args['--root-path'] or WP_PATH
    exported_sites = main_export(args)

    # docker needs an absolute path in order to mount volumes
    abs_output_dir = os.path.abspath(args['--output-dir'])

    for site_name, export_path in exported_sites.items():
        # stop running countainer first (if any)
        os.system("docker rm -f %s" % site_name)

        # run new countainer
        docker_cmd = """docker run -d \
        --name "%(site_name)s" \
        --restart=always \
        --net wp-net \
        --label "traefik.enable=true" \
        --label "traefik.backend=static-%(site_name)s" \
        --label "traefik.frontend=static-%(site_name)s" \
        --label "traefik.frontend.rule=Host:%(WP_HOST)s;PathPrefix:/%(WP_PATH)s/%(site_name)s" \
        -v %(abs_output_dir)s/%(site_name)s/html:/usr/share/nginx/html \
        nginx
        """ % {
            'site_name': site_name,
            'abs_output_dir': abs_output_dir,
            'WP_HOST': WP_HOST,
            'WP_PATH': WP_PATH,
        }
        os.system(docker_cmd)
        logging.info("Docker launched for %s", site_name)


def main_generate(args):
    sites = Utils.get_content_of_csv_file(filename="sites.csv")


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
        args['--site-url'] = WP_ADMIN_URL
    if not args['--wp-cli']:
        args['--wp-cli'] = None
    if not args['--root-path']:
        args['--root-path'] = ''
    return args


if __name__ == '__main__':

    # docopt return a dictionary with all arguments
    # __doc__ contains package docstring
    args = set_default_values(docopt(__doc__, version=VERSION))
    print(args)

    # set logging config before anything else
    set_logging_config(args)

    main(args)
