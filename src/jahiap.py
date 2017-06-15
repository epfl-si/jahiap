"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import argparse
import logging
import os
import pickle
import zipfile
import requests

from pprint import pprint, pformat
from datetime import datetime

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
    if args.output_dir:
        if not os.path.isdir(args.output_dir):
            os.makedirs(args.output_dir)
    else:
        raise SystemExit("Ouput '%s' does not exist. Please create it first" % args.output_dir)

    # forward to appropriate main function
    args.command(args)


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
        output_subdir = os.path.join(args.output_dir, site_name)
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
        output_subdir = os.path.join(args.output_dir, site_name)

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
        output_subdir = os.path.join(args.output_dir, site.name)

        if args.clean_wordpress:
            wp_exporter = WPExporter(site=site, domain=args.site_url)
            wp_exporter.delete_all_content()
            logging.info("Data of Wordpress site successfully deleted")

        if args.to_wordpress:
            wp_exporter = WPExporter(site=site, domain=args.site_url)
            wp_exporter.import_all_data_to_wordpress()
            logging.info("Site successfully exported to Wordpress")

        if args.to_static:
            export_path = os.path.join(
                output_subdir, "%s_html" % site.name)
            HTMLExporter(site, export_path)
            logging.info("Site successfully exported to HTML files")

        if args.to_dictionary:
            export_path = os.path.join(
                output_subdir, "%s_dict.py" % site.name)
            data = DictExporter.generate_data(site)
            pprint(data)
            with open(export_path, 'w') as output:
                output.write("%s_data = " % site.name)
                output.write(pformat(data))
                output.flush()
            logging.info("Site successfully exported to python dictionary")


if __name__ == '__main__':
    # declare parsers for command line arguments
    parser = argparse.ArgumentParser(
        description='Crawl, unzip, parse and export Jahia XML')
    subparsers = parser.add_subparsers()

    # logging-related agruments
    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        help='Set logging level to DEBUG (default is INFO)')
    parser.add_argument('--quiet',
                        dest='quiet',
                        action='store_true',
                        help='Set logging level to WARNING (default is INFO)')

    # common arguments for all commands
    parser.add_argument('site_name',
                        metavar='SITE',
                        help='site name, as per jahia key, e.g "dcsl"')
    parser.add_argument('-o', '--output-dir',
                        dest='output_dir',
                        default='build',
                        help='directory where to perform command')
    parser.add_argument('-n', '--number',
                        action='store',
                        type=int,
                        default=1,
                        help='number of sites to analyse (fetched in JAHIA_SITES, from given site name)')

    # arguments required for all by 'crawl' command
    parser.add_argument('-f', '--force',
                        dest='force',
                        action='store_true',
                        help='Force download even if exisiting files for same site')
    parser.add_argument('--date',
                        action='store',
                        default=datetime.today().strftime("%Y-%m-%d-%H-%M"),
                        help='date and time for the snapshot, e.g : 2017-01-15-23-00')

    # "crawl" command
    parser_crawl = subparsers.add_parser('crawl')
    parser_crawl.set_defaults(command=main_crawl)

    # "unzip" command
    parser_unzip = subparsers.add_parser('unzip')
    parser_unzip.set_defaults(command=main_unzip)

    # "parse" command
    parser_parse = subparsers.add_parser('parse')
    parser_parse.add_argument(
        '-r', '--print-report',
        dest='print_report',
        action='store_true',
        help='print report with parsed content')
    parser_parse.set_defaults(command=main_parse)

    # "export" command
    parser_export = subparsers.add_parser('export')
    parser_export.add_argument(
        '-w', '--to-wordpress',
        dest='to_wordpress',
        action='store_true',
        help='export parsed data to Wordpress')
    parser_export.add_argument(
        '-c', '--clean-wordpress',
        dest='clean_wordpress',
        action='store_true',
        help='delete all content of Wordpress site')
    parser_export.add_argument(
        '-s', '--to-static',
        dest='to_static',
        action='store_true',
        help='export parsed data to static HTML files')
    parser_export.add_argument(
        '-d', '--to-dictionary',
        dest='to_dictionary',
        action='store_true',
        help='export parsed data to python dictionary')
    parser_export.add_argument(
        '-u', '--site-url',
        dest='site_url',
        metavar='URL',
        default=DOMAIN,
        help='wordpress URL where to export parsed content')
    parser_export.add_argument(
        '-r', '--print-report',
        dest='print_report',
        action='store_true',
        help='print report with parsed content')
    parser_export.set_defaults(command=main_export)

    # forward to main function
    args = parser.parse_args()

    # set logging config before anything else
    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main(args)
