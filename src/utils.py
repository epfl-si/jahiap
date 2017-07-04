"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import logging
import os
import requests

import xml.dom.minidom

from bs4 import BeautifulSoup


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
        logging.basicConfig(level=level)
        logging.getLogger().setLevel(level)
