#!/usr/local/bin/python

from slugify import slugify

import xml.dom.minidom
import exporter


# the path of the Jahia Site xml data file
XML_PATH = "/home/me/Downloads/jahia/dcsl/export_en.xml"

# the output path
OUT_PATH = "/tmp/dcsl"

class Site:

    """A Jahia Site. Have 1 to N Jahia Pages"""

    pages = {}
    xml_path = ""

    def __init__(self, xml_path):

        self.xml_path = xml_path

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

            pages[page.pid] = page

            xml_boxes = xml_page.getElementsByTagName("main")

            boxes = []

            for xml_box in xml_boxes:
                box = Box(xml_box)
                boxes.append(box)

            page.boxes = boxes

        self.pages = pages


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

        if "text" == self.type:
            self.content = element.getElementsByTagName("text")[0].getAttribute("jahia:value")

    def __str__(self):
        return self.type + " " + self.title


site = Site(XML_PATH)

ex = exporter.Exporter(site, OUT_PATH)


