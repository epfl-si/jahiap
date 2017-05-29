#!/usr/local/bin/python

from slugify import slugify

import xml.dom.minidom
import exporter
import os

from settings import BASE_PATH, OUT_PATH, SITE_NAME


class Utils:
    """Various utilities"""
    @staticmethod
    def get_tag_attribute(dom, tag, attribute):
        """Returns the given attribute of the given tag"""
        return dom.getElementsByTagName(tag)[0].getAttribute(attribute)


class Site:
    """A Jahia Site. Have 1 to N Pages"""

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

        # the sidebar
        self.sidebar = Sidebar()

        # parse the data
        self.parse_data()

        # generate the report
        self.report = ""

        self.generate_report()

    def parse_data(self):
        """Parse the Site data"""

        # load the xml
        xml_file = open(self.xml_path, "r")

        dom = xml.dom.minidom.parseString(xml_file.read())

        # do the parsing
        self.parse_site_params(dom)
        self.parse_pages(dom)
        self.parse_sidebar(dom)
        self.parse_files()

    def parse_site_params(self, dom):
        """Parse the site params"""
        self.title = Utils.get_tag_attribute(dom, "siteName", "jahia:value")
        self.theme = Utils.get_tag_attribute(dom, "theme", "jahia:value")
        self.acronym = Utils.get_tag_attribute(dom, "acronym", "jahia:value")
        self.css_url = "//static.epfl.ch/v0.23.0/styles/%s-built.css" % self.theme

    def parse_pages(self, dom):
        """Parse the pages"""
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

    def parse_sidebar(self, dom):
        """Parse the sidebar"""
        extra = dom.getElementsByTagName("extra")

        for element in extra:
            box = Box(element)
            self.sidebar.boxes.append(box)

    def parse_files(self):
        """Parse the files"""
        start = "%s/content/sites/%s/files" % (BASE_PATH, SITE_NAME)

        for (path, dirs, files) in os.walk(start):
            for file in files:
                # we exclude the thumbnails
                if "thumbnail" == file or "thumbnail2" == file:
                    continue

                file = File(name=file, path=path)

                self.files.append(file)

    def include_box(self, xml_box, page):
        """Check if the given box belongs to the given page"""

        parent = xml_box.parentNode

        while "jahia:page" != parent.nodeName:
            parent = parent.parentNode

        return page.pid == parent.getAttribute("jahia:pid")

    def generate_report(self):
        """Generate the report of what has been parsed"""

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
Found :

  - %s files

  - %s pages :

""" % (num_files, num_pages)

        for num, count in num_boxes.items():
            self.report += "    - %s %s boxes\n" % (count, num)


class Sidebar:
    """A Jahia Sidebar"""

    boxes = []


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
        "epfl:coloredTextBox": "coloredText",
        "epfl:infoscienceBox": "infoscience",
    }

    def __init__(self, element):
        self.set_type(element)
        self.title = Utils.get_tag_attribute(element, "boxTitle", "jahia:value")
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
        if "text" == self.type or "coloredText" == self.type:
            self.content = Utils.get_tag_attribute(element, "text", "jahia:value")

            # fix the links
            old = "###file:/content/sites/%s/files/" % SITE_NAME
            new = "/files/"

            self.content = self.content.replace(old, new)

        # infoscience
        elif "infoscience" == self.type:
            url = Utils.get_tag_attribute(element, "url", "jahia:value")

            self.content = "[infoscience url=%s]" % url

    def __str__(self):
        return self.type + " " + self.title


class File:
    """A Jahia File"""

    def __init__(self, name, path):
        self.name = name
        self.path = path


site = Site(BASE_PATH + "/export_en.xml")

print(site.report)

ex = exporter.Exporter(site, OUT_PATH)
