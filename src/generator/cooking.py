""" (c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017
cooking: tool to generate composition for all sites (and start them up)

Usage:
cooking.py cut   <CSV_FILE> [--conf-path=<CONF_PATH>] [--recurse --force] [--debug | --quiet]
cooking.py cook  <CONF_PATH> [--output-path=<OUTPUT_PATH>] [--recurse --force] [--debug | --quiet]

Options:
  -h, --help                  Show this help message and exit
  -v --version                Show version.
  --conf-path=<CONF_PATH>     Path where to export yaml files [default: build/etc]
  --output-path=<OUTPUT_PATH> Path where to create compositions [default: build/sites]
  -r, --recurse               Recurse on every YAML files found in <CONF_PATH> [default: False]
  -f, --force                 Force generation and override exisiting files [default: False]
  --debug                     Set logging level to DEBUG (default is INFO)
  --quiet                     Set logging level to WARNING (default is INFO)
"""
import os
import csv
import logging

from docopt import docopt
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
from jinja2 import Environment, PackageLoader


from generator.utils import Utils as GeneratorUtils


VERSION = 0.2

WP_HOST = os.environ.get("WP_HOST")


def main(args):
    logging.info("Starting cooking script...")
    logging.debug(args)

    if args['cut']:
        prepare_ingredients(args)
    if args['cook']:
        cook_all_sites(args)


def prepare_ingredients_one_site(csv_info):

    # load template
    env = Environment(
        loader=PackageLoader('generator', 'templates'))

    site_name = csv_info['site_name']
    parent = csv_info['parent']

    # build yml file
    template = env.get_template('conf.yaml')
    content = template.render(wp_host=WP_HOST, **csv_info)

    # build file path
    if parent == 'root':
        dir_path = args['--conf-path']
    else:
        dir_path = os.path.join(args['--conf-path'], parent)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    file_path = os.path.join(dir_path, site_name) + ".yaml"

    # write yml file
    with open(file_path, 'w') as output:
        output.write(content)
        output.flush()
        logging.info("(ok) %s", file_path)


def prepare_ingredients(args):
    # check config
    GeneratorUtils.validate_dir(args['--conf-path'], args['--force'])

    # load template
    env = Environment(
        loader=PackageLoader('generator', 'templates'))

    with open(args['<CSV_FILE>']) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # row is a dictionnary with the following keys:
            # site_name;parent;type_name;site_url;site_title;email;username;pwd;db_name
            site_name = row['site_name']
            parent = row['parent']

            # build yml file
            template = env.get_template('conf.yaml')
            content = template.render(wp_host=WP_HOST, **row)

            # build file path
            if parent == 'root':
                dir_path = args['--conf-path']
            else:
                dir_path = os.path.join(args['--conf-path'], parent)
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)
            file_path = os.path.join(dir_path, site_name) + ".yaml"

            # write yml file
            with open(file_path, 'w') as output:
                output.write(content)
                output.flush()
                logging.info("(ok) %s", file_path)


def cook_all_sites(args):
    # check output
    GeneratorUtils.validate_dir(args['--output-path'], args['--force'])

    # check config
    if not os.path.exists(args['<CONF_PATH>']):
        raise SystemExit("Config '%s' does not exist." % args['<CONF_PATH>'])

    if os.path.isfile(args['<CONF_PATH>']):
        # config path points to a file : single generation
        cook_one_site(args, args['<CONF_PATH>'])
    else:
        # config path points to a dir : multiple generation
        if args['--recurse']:
            # generate sites for all yaml files found recursively
            for root, dirs, files in os.walk(args['<CONF_PATH>']):
                config_files = [file_name for file_name in files
                                if file_name.endswith('.yaml')]
                for config_file in config_files:
                    config_path = os.path.join(root, config_file)
                    cook_one_site(args, config_path)
        else:
            # generate sites for all yaml files in args['<CONF_PATH>'] dir
            config_files = [file_name for file_name
                            in os.listdir(args['<CONF_PATH>'])
                            if file_name.endswith('.yaml')]
            for config_file in config_files:
                config_path = os.path.join(args['<CONF_PATH>'], config_file)
                cook_one_site(args, config_path)


def cook_one_site(args, config_file):
    """
        Create project from the template. See API reference online:
        https://cookiecutter.readthedocs.io/en/latest/cookiecutter.html#module-cookiecutter.main
    """
    logging.info("Starting cookiecutter...")
    try:
        site_path = cookiecutter(
            '.',
            no_input=True,
            overwrite_if_exists=args['--force'],
            config_file=config_file,
            output_dir=args['--output-path'])
        logging.info("Site generated into %s", site_path)
    except OutputDirExistsException:
        logging.error("%s already exists. Use --force to override", config_file)


def set_default_values(args):
    """
    Set default values of arguments 'args'
    The static default values are defined to the main docstring.
    The dynamic default values are defined in this method.
    """
    # raise a warning if --force is used
    if args['--force']:
        logging.warning("You are using --force option to overwrite existing file.")

    if not args['--conf-path']:
        args['--conf-path'] = "build/etc"

    if not args['--output-path']:
        args['--output-path'] = "build/sites"

    return args


if __name__ == '__main__':

    # docopt return a dictionary with all arguments
    # __doc__ contains package docstring
    args = docopt(__doc__, version=VERSION)

    main(set_default_values(args))
