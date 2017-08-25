"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017
jahiap: a wonderful tool

Usage:
  jahiap.py crawl <site>  [--output-dir=<OUTPUT_DIR>] [--export-path=<EXPORT_PATH>]
                          [--number=<NUMBER>] [--date DATE] [--force-crawl] [--debug | --quiet]
  jahiap.py unzip <site>  [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug | --quiet]
  jahiap.py parse <site>  [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--print-report]
                          [--debug | --quiet] [--use-cache] [--site-path=<SITE_PATH>]
  jahiap.py export <site> [--clean-wordpress | --to-wordpress | --nginx-conf]
                          [--wp-cli=<WP_CLI> --site-host=<SITE_HOST> --site-path=<SITE_PATH>]
                          [--to-static --to-dictionary --number=<NUMBER> --print-report]
                          [--output-dir=<OUTPUT_DIR> --export-path=<EXPORT_PATH>]
                          [--use-cache] [--debug | --quiet]
  jahiap.py docker <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--debug | --quiet]
  jahiap.py generate <csv_file> [--output-dir=<OUTPUT_DIR>] [--conf-path=<CONF_PATH>]
                                [--cookie-path=<COOKIE_PATH>] [--processes=<PROCESSES>] [--force] [--debug | --quiet]
  jahiap.py cleanup <csv_file>  [--debug | --quiet]
  jahiap.py global_report <site> [--output-dir=<OUTPUT_DIR>] [--number=<NUMBER>] [--use-cache] [--debug | --quiet]

Options:
  -h --help                     Show this screen.
  -v --version                  Show version.
  -o --output-dir=<OUTPUT_DIR>  Directory where to perform command [default: build].
  -n --number=<NUMBER>          Number of sites to analyse (fetched in JAHIA_SITES, from given site name) [default: 1].
  --export-path=<EXPORT_PATH>   (crawl) Directory where Jahia Zip files are stored
  --date DATE                   (crawl) Date and time for the snapshot, e.g : 2017-01-15-23-00.
  --force-crawl                 (crawl) Force download even if existing snapshot for same site [default: False].
  --use-cache                   (parse) Do not parse if pickle file found with a previous parsing result
  --site-path=<SITE_PATH>       (parse, export) sub dir where to export parsed content
  -r --print-report             (FIXME) Print report with content.
  --nginx-conf                  (export) Only export pages to WordPress in order to generate nginx conf
  -s --to-static                (export) Export parsed data to static HTML files.
  -d --to-dictionary            (export) Export parsed data to python dictionary.
  -c --clean-wordpress          (export) Delete all content of WordPress site.
  -w --to-wordpress             (export) Export parsed data to WordPress and generate nginx conf
  --wp-cli=<WP_CLI>             (export) Name of wp-cli container to use with given WordPress URL. (default WPExporter)
  --recurse                     (compose|cleanup) Search in all the tree of directories
  --site-host=<SITE_HOST>       (export) WordPress HOST where to export parsed content. (default is $WP_ADMIN_URL)
  --conf-path=<CONF_PATH>       (generate) Path where to export yaml files [default: build/etc]
  --cookie-path=<COOKIE_PATH>   (generate) Path where {{ cookiecutter project }} is located [default is $COOKIE_PATH]
  -f --force                    (*) Force unzip, export, generate
  --debug                       (*) Set logging level to DEBUG (default is INFO).
  --quiet                       (*) Set logging level to WARNING (default is INFO).
"""
import logging
import os
import pickle
import sys
import csv
import timeit
from collections import OrderedDict
from datetime import datetime, timedelta
from pprint import pprint, pformat

from docopt import docopt

from utils import Utils
from generator.utils import Utils as UtilsGenerator
from crawler import SiteCrawler
from exporter.dict_exporter import DictExporter
from exporter.html_exporter import HTMLExporter
from exporter.wp_exporter import WPExporter
from wordpress_json import WordpressError
from generator.tree import Tree
from unzipper.unzip import unzip_one
from parser.jahia_site import Site
from settings import VERSION, EXPORT_PATH, WP_HOST, WP_PATH, \
    LINE_LENGTH_ON_EXPORT, LINE_LENGTH_ON_PPRINT


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
            method_name = 'main_' + str(key)
            return getattr(sys.modules[__name__], method_name)(args)


def main_crawl(args):
    site = args['<site>']

    logging.info("starting crawling...")
    start_time = timeit.default_timer()
    SiteCrawler.download(args)
    elapsed = timedelta(seconds=timeit.default_timer() - start_time)
    logging.info("Jahia ZIP {} downloaded in {}".format(site, elapsed))

    logging.info("starting creating static site {}".format(site))
    sites = UtilsGenerator.csv_to_dict("csv-data/all.csv", delimiter=";")
    for current_site in sites:
        if current_site['name'] == site:
            site_url = current_site['site_url']
            break

    start_time = timeit.default_timer()
    Utils.create_static_site(site_url)
    elapsed = timedelta(seconds=timeit.default_timer() - start_time)
    logging.info("Static Site {} created in {}".format(site_url, elapsed))


def main_unzip(args):
    # get zip files according to args
    zip_files = SiteCrawler.download(args)

    # to store paths of downloaded zips
    unzipped_files = OrderedDict()

    for site_name, zip_file in zip_files.items():
        try:
            unzipped_files[site_name] = unzip_one(args['--output-dir'], site_name, zip_file)
        except Exception as err:
            logging.error("%s - unzip - Could not unzip file - Exception: %s", site_name, err)

    # return results
    return unzipped_files


def main_parse(args):
    # get list of sites to parse according to args
    site_dirs = main_unzip(args)

    # to store paths of parsed objects
    parsed_sites = OrderedDict()

    for site_name, site_dir in site_dirs.items():
        try:
            # create subdir in output_dir
            output_subdir = os.path.join(args['--output-dir'], site_name)

            # where to cache our parsing
            pickle_file = os.path.join(output_subdir, 'parsed_%s.pkl' % site_name)

            # when using-cache: check if already parsed
            if args['--use-cache']:
                if os.path.exists(pickle_file):
                    with open(pickle_file, 'rb') as input:
                        logging.info("Loaded parsed site from %s" % pickle_file)
                        parsed_sites[site_name] = pickle.load(input)
                        continue

            # FIXME : site-path should be given in exporter, not parser
            root_path = ""
            # if args['--site-path']:
            #   root_path = "/%s/%s" % (args['--site-path'], site_name)
            #   logging.info("Setting root_path %s", root_path)
            logging.info("Parsing Jahia xml files from %s...", site_dir)
            site = Site(site_dir, site_name, root_path=root_path)

            print(site.report)

            # always save the parsed data on disk, so we can use the
            # cache later if we want
            with open(pickle_file, 'wb') as output:
                logging.info("Parsed site saved into %s" % pickle_file)
                pickle.dump(site, output, pickle.HIGHEST_PROTOCOL)

            # log success
            logging.info("Site %s successfully parsed" % site_name)
            parsed_sites[site_name] = site

        except Exception as err:
            logging.error("%s - parse - Exception: %s", site_name, err)

    # return results
    return parsed_sites


def main_global_report(args):
    "Generate a global report with stats like the number of pages, files and boxes"
    path = os.path.join(args['--output-dir'], "global-report.csv")

    logging.info("Generating global report at %s" % path)

    sites = main_parse(args)

    # retrieve all the box types
    box_types = set()

    for site_name, site in sites.items():
        for key in site.num_boxes.keys():
            if key:
                box_types.add(key)

    # the base field names for the csv
    fieldnames = ["name", "pages", "files"]

    # add all the box types
    fieldnames.extend(sorted(box_types))

    # write the csv file
    with open(path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # header
        writer.writeheader()

        # content
        for site_name, site in sites.items():
            writer.writerow(site.get_report_info(box_types))


def main_export(args):
    # get list of parsed sites

    sites = main_parse(args)

    wp_cli = None
    if '--wp-cli' in args:
        wp_cli = args['--wp-cli']

    # to store results of exported parsed sites
    exported_sites = OrderedDict()

    for site_name, site in sites.items():
        try:

            # store results
            exported_site = {}
            exported_sites[site_name] = exported_site

            # create subdir in output_dir
            output_subdir = os.path.join(args['--output-dir'], site.name)

            try:
                if args['--clean-wordpress']:
                    logging.info("Cleaning WordPress for %s...", site.name)
                    wp_exporter = WPExporter(
                        site,
                        site_host=args['--site-host'],
                        site_path=args['--site-path'],
                        output_dir=args['--output-dir'],
                        wp_cli=wp_cli
                    )
                    wp_exporter.delete_all_content()
                    logging.info("Data of WordPress site %s successfully deleted", site.name)

                if args['--to-wordpress']:

                    logging.info("Exporting %s to WordPress...", site.name)
                    wp_exporter = WPExporter(
                        site,
                        site_host=args['--site-host'],
                        site_path=args['--site-path'],
                        output_dir=args['--output-dir'],
                        wp_cli=wp_cli
                    )
                    wp_exporter.import_all_data_to_wordpress()
                    exported_site['wordpress'] = args['--site-path']
                    logging.info("Site %s successfully exported to WordPress", site.name)

                if args['--nginx-conf']:

                    logging.info("Creating nginx conf for %s...", site.name)
                    wp_exporter = WPExporter(
                        site,
                        site_host=args['--site-host'],
                        site_path=args['--site-path'],
                        output_dir=args['--output-dir'],
                        wp_cli=wp_cli
                    )
                    wp_exporter.import_all_data_to_wordpress()
                    wp_exporter.generate_nginx_conf_file()
                    exported_site['wordpress'] = args['--site-path']
                    logging.info("Nginx conf for %s successfully generated", site.name)
            except WordpressError as err:
                logging.error("%s - WP export - WordPress not available: %s", site.name, err)

            if args['--to-static']:
                logging.info("Exporting %s to static website...", site.name)
                export_path = os.path.join(output_subdir, "html")
                HTMLExporter(site, export_path)
                exported_site['static'] = export_path
                logging.info("Site %s successfully exported to static website", site.name)

            if args['--to-dictionary']:
                logging.info("Exporting %s to python dictionary...", site.name)
                export_path = os.path.join(
                    output_subdir, "%s_dict.py" % site.name)
                data = DictExporter.generate_data(site)
                pprint(data, width=LINE_LENGTH_ON_PPRINT)
                with open(export_path, 'w') as output:
                    output.write("%s_data = " % site.name)
                    output.write(pformat(data, width=LINE_LENGTH_ON_EXPORT))
                    output.flush()
                exported_site['dict'] = export_path
                logging.info("Site %s successfully exported to python dictionary", site.name)
        except Exception as err:
            logging.error("%s - export - Error exporting site: %s", site_name, err)

        if args['--to-wordpress'] and int(args['--number']) > 1:
            wp_exporter = WPExporter(
                site,
                site_host=args['--site-host'],
                site_path=args['--site-path'],
                output_dir=args['--output-dir'],
                wp_cli=wp_cli
            )
            wp_exporter.delete_all_content()
            logging.info("Data of Wordpress site successfully deleted")

    # overall result : {site_name: {wordpress: URL, static: PATH, dict: PATH}, ...}
    return exported_sites


def main_docker(args):
    # This command depends on traefik running
    if not Utils.is_traefik_running():
        raise SystemExit("You need to run treafik in order to spawn a container")

    # get list of sites html static sites
    args['--to-static'] = True
    exported_sites = main_export(args)

    # docker needs an absolute path in order to mount volumes
    abs_output_dir = os.path.abspath(args['--output-dir'])
    abs_nginx_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "nginx"))

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
        -v %(abs_nginx_dir)s/nginx.conf:/etc/nginx/conf.d/default.conf \
        nginx
        """ % {
            'site_name': site_name,
            'abs_output_dir': abs_output_dir,
            'abs_nginx_dir': abs_nginx_dir,
            'WP_HOST': WP_HOST,
            'WP_PATH': WP_PATH,
        }
        os.system(docker_cmd)
        logging.info("Docker launched for %s", site_name)


def main_generate(args):

    tree = Tree(args, sites=UtilsGenerator.csv_to_dict(file_path=args['<csv_file>']))
    tree.prepare_run()
    tree.run(processes=int(args["--processes"]))


def main_cleanup(args):

    tree = Tree(args, sites=UtilsGenerator.csv_to_dict(file_path=args['<csv_file>']))
    tree.cleanup()


def set_default_values(args):
    """
    Set default values of arguments 'args'
    The static default values are defined to the main docstring.
    The dynamic default values are defined in this method.
    """
    # Set default values
    if not args['--date']:
        args['--date'] = datetime.today().strftime("%Y-%m-%d-%H-%M")
    if not args['--wp-cli']:
        args['--wp-cli'] = None
    if not args['--export-path']:
        args['--export-path'] = EXPORT_PATH
    if not isinstance(args['--site-path'], str):
        args['--site-path'] = WP_PATH
    if not args['--site-host']:
        args['--site-host'] = WP_HOST
    if args['--force']:
        logging.warning("You are using --force option to overwrite existing file.")
    if not args['--conf-path']:
        args['--conf-path'] = "build/etc"
    if not args['--cookie-path']:
        args['--cookie-path'] = Utils.get_required_env('COOKIE_PATH')

    return args


if __name__ == '__main__':

    # docopt return a dictionary with all arguments
    # __doc__ contains package docstring
    args = set_default_values(docopt(__doc__, version=VERSION))

    # set logging config before anything else
    Utils.set_logging_config(args)

    logging.debug(args)

    main(args)
