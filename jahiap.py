#!/usr/local/bin/python

from slugify import slugify

import xml.dom.minidom
import exporter
import os

from settings import *


class Site:

    """A Jahia Site. Have 1 to N Jahia Pages"""

    def __init__(self, xml_path):

        self.xml_path = xml_path

        # site params that are parsed later
        self.title = ""
        self.acronym = ""
        self.theme = ""
        self.css_url = ""

        # the pages. The dict key is the page id, the dict value is the page itself
        self.pages = {}

        # the files
        self.files = []

        # parse the data
        self.parse_data()

        # generate the report
        self.report = ""

        self.generate_report()

    def parse_data(self):
        """
        Parse the Site data
        """

        xml_file = open(self.xml_path, "r")

        dom = xml.dom.minidom.parseString(xml_file.read())

        self.title = dom.getElementsByTagName("siteName").getAttribute("jahia:value")
        self.theme = dom.getElementsByTagName("theme").getAttribute("jahia:value")
        self.acronym = dom.getElementsByTagName("acronym").getAttribute("jahia:value")
        self.css_url = "//static.epfl.ch/v0.23.0/styles/%s-built.css" % self.theme

        xml_pages = dom.getElementsByTagName("jahia:page")

        # parse the pages
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

        # parse the files
        File.parse_files(self)

    def include_box(self, xml_box, page):
        """Check if the given box belongs to the given page"""

        parent = xml_box.parentNode

        while "jahia:page" != parent.nodeName:
            parent = parent.parentNode

        return page.pid == parent.getAttribute("jahia:pid")

    def generate_report(self):
        """Generate the report of what have been parsed"""

        num_files = len(self.files)

        num_pages = len(self.pages)

        # calculate the total number of boxes by type
        # dict key is the box type, dict value is the number of boxes
        num_boxes = {}

        for page in self.pages.values():
            for box in page.boxes:
                if box.type in num_boxes:
                    num_boxes[box.type] = num_boxes[box.type] + 1
                else:
                    num_boxes[box.type] = 1

        self.report = """
Parsed :

  - %s files 
  
  - %s pages :
  
""" % (num_files, num_pages)

        for num, count in num_boxes.items():
            self.report += "    - %s %s boxes\n" % (count, num)


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


class File:
    """A Jahia File"""

    def __init__(self, name, path):
        self.name = name
        self.path = path

    @staticmethod
    def parse_files(site):
        """Parse the site files"""
        start = "%s/content/sites/%s/files" % (BASE_PATH, SITE_NAME)

        for (path, dirs, files) in os.walk(start):
            for file in files:
                # we exclude the thumbnails
                if "thumbnail" == file or "thumbnail2" == file:
                    continue

                file = File(name=file, path=path)

                site.files.append(file)


site = Site(BASE_PATH + "/export_en.xml")

print(site.report)

ex = exporter.Exporter(site, OUT_PATH)
