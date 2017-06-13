"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
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