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


def main(parser, args):
    """
        Setup context (e.g debug level) and forward to command-dedicated main function
    """
    logging.info("Starting jahiap script...")

    # mkdir from output_dir or as temporary dir
    if args.output_dir:
        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)
    else:
        raise SystemExit("Ouput '%s' does not exist. Please create it first" % args.output_dir)

    # forward to appropriate main function
    args.command(parser, args)


def main_crawl(parser, args):
    logging.info("starting crawling...")
    try:
        SiteCrawler.download(args)
    except requests.ConnectionError as err:
        logging.error(err)


def main_unzip(parser, args):
    logging.info("Unzipping %s..." % args.zip_file)

    # make sure we have an input file
    if not args.zip_file or not os.path.isfile(args.zip_file):
        parser.print_help()
        raise SystemExit("Jahia zip file not found")

    # create zipFile to manipulate / extract zip content
    export_zip = zipfile.ZipFile(args.zip_file, 'r')

    # find the zip containing the site files
    zips = [name for name in export_zip.namelist() if name.endswith(".zip") and name != "shared.zip"]
    if len(zips) != 1:
        logging.error("Should have one and only one zip file in %s" % zips)
        raise SystemExit("Could not find appropriate zip with files")
    zip_with_files = zips[0]

    # extract the export zip file
    export_zip.extractall(args.output_dir)
    export_zip.close()

    # get the site name
    site_name = zip_with_files[:zip_with_files.index(".")]

    base_path = os.path.join(args.output_dir, site_name)

    # unzip the zip with the files
    zip_path = os.path.join(args.output_dir, zip_with_files)
    zip_ref_with_files = zipfile.ZipFile(zip_path, 'r')
    zip_ref_with_files.extractall(base_path)

    # return site path & name
    logging.info("Site successfully extracted in %s" % base_path)
    return (base_path, site_name)


def main_parse(parser, args):
    logging.info("Parsing...")

    base_path = os.path.join(args.output_dir, args.site_name)

    site = Site(base_path, args.site_name)

    if args.print_report:
        print(site.report)

    # save parsed site on file system
    file_name = os.path.join(
        args.output_dir,
        'parsed_%s.pkl' % args.site_name)

    with open(file_name, 'wb') as output:
        pickle.dump(site, output, pickle.HIGHEST_PROTOCOL)

    # return site object
    logging.info("Site successfully parsed, and saved into %s" % file_name)
    return site


def main_export(parser, args):
    # restore parsed site from file system
    file_name = os.path.join(
        args.output_dir,
        'parsed_%s.pkl' % args.site_name)
    if os.path.exists(file_name):
        with open(file_name, 'rb') as input:
            site = pickle.load(input)
        logging.info("Loaded parsed site from %s" % file_name)
    # or parse it again
    else:
        args.print_report = False
        site = main_parse(parser, args)

    logging.info("Exporting...")

    if args.to_wordpress:
        wp_exporter = WPExporter(site=site, domain=args.site_url)
        wp_exporter.import_all_data_in_wordpress()
        logging.info("Site successfully exported to Wordpress")

    if args.to_static:
        export_path = os.path.join(
            args.output_dir, "%s_html" % args.site_name)
        HTMLExporter(site, export_path)
        logging.info("Site successfully exported to HTML files")

    if args.to_dictionary:
        export_path = os.path.join(
            args.output_dir, "%s_dict.py" % args.site_name)
        data = DictExporter.generate_data(site)
        pprint(data)
        with open(export_path, 'w') as output:
            output.write("%s_data = " % args.site_name)
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
    parser.add_argument('-o', '--output-dir',
                        dest='output_dir',
                        help='directory where to perform command')

    # "crawl" command
    parser_crawl = subparsers.add_parser('crawl')
    parser_crawl.set_defaults(command=main_crawl)

    parser_crawl.add_argument('--site',
                        action='store',
                        help='site name (in jahia admin) of site to get the zip for')
    parser_crawl.add_argument('-f', '--force',
                        dest='force',
                        action='store_true',
                        help='Force download even if exisiting files for same site')
    parser_crawl.add_argument('-d', '--date',
                        action='store',
                        default=datetime.today().strftime("%Y-%m-%d-%H-%M"),
                        help='date and time for the snapshot, e.g : 2017-01-15-23-00')
    parser_crawl.add_argument('-n', '--number',
                        action='store',
                        type=int,
                        default=1,
                        help='number of sites to crawl in JAHIA_SITES')
    parser_crawl.add_argument('-s', '--start-at',
                        action='store',
                        dest='start_at',
                        type=int,
                        default=0,
                        help='(zero-)index where to start in JAHIA_SITES')

    # "unzip" command
    parser_unzip = subparsers.add_parser('unzip')
    parser_unzip.add_argument('zip_file', help='path to Jahia XML file')
    parser_unzip.set_defaults(command=main_unzip)

    # "parse" command
    parser_parse = subparsers.add_parser('parse')
    parser_parse.add_argument(
        'site_name',
        help='name of sub directories that contain the site files')
    parser_parse.add_argument(
        '-r', '--print-report',
        dest='print_report',
        action='store_true',
        help='print report with parsed content')
    parser_parse.set_defaults(command=main_parse)

    # "export" command
    parser_export = subparsers.add_parser('export')
    parser_export.add_argument(
        'site_name',
        help='name of sub directories that contain the site files')
    parser_export.add_argument(
        '-w', '--to-wordpress',
        dest='to_wordpress',
        action='store_true',
        help='export parsed data to Wordpress')
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

    main(parser, args)
