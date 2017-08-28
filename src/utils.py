"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import logging
import os
import xml.dom.minidom

import requests
from bs4 import BeautifulSoup
from fabric.api import env, cd, run
from fabric.contrib.files import exists

from urllib.parse import urlsplit


class Utils:
    # the cache with all the doms
    dom_cache = {}

    """Various utilities"""
    @staticmethod
    def get_tag_attribute(dom, tag, attribute):
        """Returns the given attribute of the given tag"""
        elements = dom.getElementsByTagName(tag)

        if not elements:
            return ""

        return elements[0].getAttribute(attribute)

    @classmethod
    def get_dom(cls, path):
        """Returns the dom of the given XML file path"""

        # we check the cache first
        if path in cls.dom_cache:
            return cls.dom_cache[path]

        # load the xml
        xml_file = open(path, "r")

        # we use BeautifulSoup first because some XML files are invalid
        xml_soup = BeautifulSoup(xml_file.read(), 'xml')

        dom = xml.dom.minidom.parseString(str(xml_soup))

        # save in the cache
        cls.dom_cache[path] = dom

        return dom

    @classmethod
    def is_traefik_running(cls):
        try:
            from settings import WP_HOST
            return requests.get("http://%s:8080" % WP_HOST).status_code == 200
        except requests.ConnectionError:
            return False

    @staticmethod
    def get_optional_env(key, default):
        """
        Return the value of an optional environment variable, and use
        the provided default if it's not set.
        """

        if not os.environ.get(key):
            logging.warning("The optional environment variable %s is not set, using '%s' as default" % (key, default))

        return os.environ.get(key, default)

    @classmethod
    def get_required_env(self, key):
        """
        Return the value of a required environment variable. If it's not
        set an exception is raised.
        """

        if not os.environ.get(key):
            raise SystemExit("The required environment variable %s is not set" % key)

        return os.environ.get(key)

    @staticmethod
    def set_logging_config(args):
        """
        Set logging with the 'good' level
        """
        level = logging.INFO
        if args['--quiet']:
            level = logging.WARNING
        elif args['--debug']:
            level = logging.DEBUG
        logging.basicConfig()
        logger = logging.getLogger()
        logger.setLevel(level)
        # set up logging to file
        fh = logging.FileHandler(Utils.get_optional_env('LOGGING_FILE', 'jahiap.log'))
        fh.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(fh)

    @staticmethod
    def create_static_site(site_url):
        """
        Create static site via wget command
        """
        env.host_string = "team@idevingsrv4.epfl.ch"
        env.static_root_dir = "/var/www/html"

        with cd(env.static_root_dir):

            # extract the domain name
            domain = urlsplit(site_url).netloc

            # delete the old static site folder
            if exists(domain):
                logging.debug("Deleting the old static site folder")
                try:
                    run("rm -rf {}".format(domain))
                except:
                    logging.error("Deleting static site {} failed".format(domain))

            # wget the static site
            logging.debug("WGet the site {}".format(domain))
            try:
                run("wget -p -k -E -m -e robots=off -w 2 --no-parent {}".format(site_url))
            except Exception as e:
                logging.error("Creating static site {} failed - Exception: {}".format(site_url, e))
