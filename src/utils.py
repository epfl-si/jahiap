"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

import xml.dom.minidom


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

        dom = xml.dom.minidom.parseString(xml_file.read())

        # save in the cache
        cls.dom_cache[path] = dom

        return dom

    @staticmethod
    def get_domain():
        """
        Return the domain name
        """
        env_var = 'WP_ADMIN_URL'
        if env_var not in os.environ:
            raise SystemExit("You must set environment variable %s" % env_var)
        else:
            return os.environ.get(env_var)

    @staticmethod
    def escape_quotes(str):
        return str.replace('"', '\\"')
