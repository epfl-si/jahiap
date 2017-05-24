#!/usr/local/bin/python

from slugify import slugify

import xml.dom.minidom
import exporter

from settings import *


class Site:

    """A Jahia Site. Have 1 to N Jahia Pages"""

    def __init__(self, xml_path):

        self.xml_path = xml_path

        # the Site pages. Key is the pid, value is the page itself
        self.pages = {}

        # TODO parse the site title
        self.title = "DATA CENTER SYSTEMS LABORATORY DCSL"

        # TODO the css is specific for the site faculty
        self.css = "//static.epfl.ch/v0.23.0/styles/ic-built.css"

        self.load_data()

    def load_data(self):
        """
        Generates the yaml file
        """

        file = open(self.xml_path, "r")

        dom = xml.dom.minidom.parseString(file.read())

        xml_pages = dom.getElementsByTagName("jahia:page")

        pages = {}

        for xml_page in xml_pages:

            page = Page(xml_page)

            # we don't include the sitemap as it's not a real page
            if "sitemap" == page.template:
                continue

            pages[page.pid] = page

            xml_boxes = xml_page.getElementsByTagName("main")

            boxes = []

            for xml_box in xml_boxes:

                if not self.include_box(xml_box, page):
                    continue

                box = Box(xml_box)
                boxes.append(box)

            page.boxes = boxes

        self.pages = pages

    def include_box(self, xml_box, page):
        """Check if the given box belongs to the given page"""

        parent = xml_box.parentNode

        while "jahia:page" != parent.nodeName:
            parent = parent.parentNode

        return page.pid == parent.getAttribute("jahia:pid")

class Page:

    """A Jahia Page. Has 1 to N Jahia Boxes"""

    boxes = []

    def __init__(self, element):
        self.pid = element.getAttribute("jahia:pid")
        self.template = element.getAttribute("jahia:template")
        self.title = element.getAttribute("jahia:title")

        if "home" == self.template:
            self.name = "index.html"
        else:
            self.name = slugify(self.title) + ".html"

    def __str__(self):
        return self.pid + " " + self.template + " " + self.title


class Box:

    """A Jahia Box. Can be of type text, infoscience, etc."""

    # the box type
    type = "unknown"
    content = ""

    # the known box types
    types = {
        "epfl:textBox": "text",
        "epfl:infoscienceBox": "infoscience",
    }

    def __init__(self, element):
        self.set_type(element)
        self.title = element.getElementsByTagName("boxTitle")[0].getAttribute("jahia:value")
        self.set_content(element)

    def set_type(self, element):
        """
        Sets the box type
        """

        type = element.getAttribute("jcr:primaryType")

        if self.types[type]:
            self.type = self.types[type]

    def set_content(self, element):

        # text
        if "text" == self.type:
            self.content = element.getElementsByTagName("text")[0].getAttribute("jahia:value")

            # fix the links
            old = "###file:/content/sites/%s/files/" % SITE_NAME
            new = "/files/"

            self.content = self.content.replace(old, new)

        # infoscience
        elif "infoscience" == self.type:

            url = element.getElementsByTagName("url")[0].getAttribute("jahia:value")

            self.content = "[infoscience url=%s]" % url


    def __str__(self):
        return self.type + " " + self.title


site = Site(BASE_PATH + "/export_en.xml")

ex = exporter.Exporter(site, OUT_PATH)
