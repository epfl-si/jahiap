"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import getopt
import os
import sys
import xml.dom.minidom
import zipfile
import tempfile
import shutil

from slugify import slugify

from exporter import Exporter
from wp_exporter import WP_Exporter


class Utils:
    """Various utilities"""
    @staticmethod
    def get_tag_attribute(dom, tag, attribute):
        """Returns the given attribute of the given tag"""
        elements = dom.getElementsByTagName(tag)

        if not elements:
            return ""

        return elements[0].getAttribute(attribute)


class Site:
    """A Jahia Site. Have 1 to N Pages"""

    def __init__(self, base_path, name):
        self.base_path = base_path
        self.name = name
        self.xml_path = base_path + "/export_en.xml"

        # site params that are parsed later
        self.title = ""
        self.acronym = ""
        self.theme = ""
        self.css_url = ""

        # the pages.
        self.pages = []

        # set for conveniency, to avoid:
        #   [p for p in self.pages if p.is_homepage()][0]
        self.homepage = None

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

        pages = []

        for xml_page in xml_pages:

            page = Page(xml_page)

            # we don't include the sitemap as it's not a real page
            if "sitemap" == page.template:
                continue

            # flag out homepage for conveniency purppose
            if page.is_homepage():
                self.homepage = page

            pages.append(page)

            xml_boxes = xml_page.getElementsByTagName("main")

            boxes = []

            for xml_box in xml_boxes:

                # Check if the box belongs to the current page
                if not self.include_box(xml_box, page):
                    continue

                # Check if xml_box contains many boxes
                multibox = xml_box.getElementsByTagName("text").length > 1
                box = Box(self, xml_box, multibox=multibox)
                boxes.append(box)

            page.boxes = boxes

        self.pages = pages

    def parse_sidebar(self, dom):
        """Parse the sidebar"""
        extra = dom.getElementsByTagName("extra")

        for element in extra:
            box = Box(self, element)
            self.sidebar.boxes.append(box)

    def parse_files(self):
        """Parse the files"""
        start = "%s/content/sites/%s/files" % (self.base_path, self.name)

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

        for page in self.pages:
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

        if self.is_homepage():
            self.name = "index.html"
        else:
            self.name = slugify(self.title) + ".html"

    def __str__(self):
        return self.pid + " " + self.template + " " + self.title

    def is_homepage(self):
        """
        Return True if the page is the homepage of site
        """
        return self.template == "home"


class Box:
    """A Jahia Box. Can be of type text, infoscience, etc."""

    # the box type
    type = ""
    # the box content
    content = ""

    # the known box types
    types = {
        "epfl:textBox": "text",
        "epfl:coloredTextBox": "coloredText",
        "epfl:infoscienceBox": "infoscience",
        "epfl:actuBox": "actu"
    }

    def __init__(self, site, element, multibox=False):
        self.site = site
        self.set_type(element)
        self.title = Utils.get_tag_attribute(element, "boxTitle", "jahia:value")
        self.set_content(element, multibox)

    def set_type(self, element):
        """
        Sets the box type
        """

        type = element.getAttribute("jcr:primaryType")

        if type in self.types:
            self.type = self.types[type]
        else:
            self.type = "unknown '" + type + "'"

    def set_content(self, element, multibox=False):
        """set the box attributes"""

        # text
        if "text" == self.type or "coloredText" == self.type:
            self.set_box_text(element, multibox)
        # infoscience
        elif "infoscience" == self.type:
            self.set_box_infoscience(element)
        # actu
        elif "actu" == self.type:
            self.set_box_actu(element)

    def set_box_text(self, element, multibox=False):
        """set the attributes of a text box"""

        if not multibox:
            self.content = Utils.get_tag_attribute(element, "text", "jahia:value")
        else:
            # Concatenate HTML content of many boxes
            content = ""
            elements = element.getElementsByTagName("text")
            for element in elements:
                content += element.getAttribute("jahia:value")
            self.content = content

        if not self.content:
            return

        # fix the links
        old = "###file:/content/sites/%s/files/" % self.site.name
        new = "/files/"

        self.content = self.content.replace(old, new)

    def set_box_actu(self, element):
        """set the attributes of an actu box"""
        url = Utils.get_tag_attribute(element, "url", "jahia:value")

        self.content = "[actu url=%s]" % url

    def set_box_infoscience(self, element):
        """set the attributes of a infoscience box"""
        url = Utils.get_tag_attribute(element, "url", "jahia:value")

        self.content = "[infoscience url=%s]" % url

    def __str__(self):
        return self.type + " " + self.title


class File:
    """A Jahia File"""

    def __init__(self, name, path):
        self.name = name
        self.path = path


def print_usage():
    """Print the command line usage"""
    print('usage : python jahiap.py -i <export_file> -o <output_dir>')


def main(argv):
    export_file = ""
    output_dir = ""
    # avoid to hardcode domain too hard
    domain = "test-web-wordpress.epfl.ch"
    # do not force generation of static files
    generate_static_files = False

    try:
        # TODO: use optparse instead ?
        # https://docs.python.org/3.1/library/optparse.html
        opts, args = getopt.getopt(argv, "hi:o:d:")
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    # parse the opts
    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt == "-i":
            export_file = arg
        elif opt == "-o":
            output_dir = arg
        elif opt == "-d":
            domain = arg

    # make sure we have an input file
    if not export_file:
        print_usage()
        sys.exit(2)

    # check if the input file exists
    if not os.path.isfile(export_file):
        print("Cannot find export file : %s" % export_file)
        print_usage()
        sys.exit(2)

    # create static export if output_dir is given
    if output_dir:
        generate_static_files = True
        # check if the output dir exists
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
    else:
        output_dir = tempfile.mkdtemp()

    # extract the export zip file
    export_zip = zipfile.ZipFile(export_file, 'r')
    export_zip.extractall(output_dir)
    export_zip.close()

    # find the zip containing the site files
    zip_with_files = ""

    for file in os.listdir(output_dir):
        if not file.endswith(".zip"):
            continue

        if file != "shared.zip":
            zip_with_files = file
            break

    if zip_with_files == "":
        print("Could not find zip with files")
        sys.exit(2)

    # get the site name
    site_name = zip_with_files[:zip_with_files.index(".")]

    base_path = "%s/%s" % (output_dir, site_name)

    # unzip the zip with the files
    zip_ref_with_files = zipfile.ZipFile(output_dir + "/" + zip_with_files, 'r')
    zip_ref_with_files.extractall(base_path)

    site = Site(base_path, site_name)

    print(site.report)

    wp_exporter = WP_Exporter(site=site, domain=domain)
    wp_exporter.import_all_data_in_wordpress()

    # generate static files only if output_dir is provided
    if generate_static_files:
        Exporter(site, output_dir + "/html")
    # otherwise, just get rid of temporary files
    else:
        shutil.rmtree(output_dir)


if __name__ == "__main__":
    main(sys.argv[1:])
