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
from settings import DOMAIN
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

        # the pages. We have a both list and a dict.
        # The dict key is the page id, and the dict value is the page itself
        self.pages = []
        self.pages_dict = {}

        # set for convenience, to avoid:
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

        for xml_page in xml_pages:
            page = Page(self, xml_page)

            # we don't include the sitemap as it's not a real page
            if "sitemap" == page.template:
                continue

            # flag out homepage for convenience
            if page.is_homepage():
                self.homepage = page

            # add the pages to the Site
            self.pages.append(page)
            self.pages_dict[page.pid] = page

            # main tag is the parent of all boxes types
            main_elements = xml_page.getElementsByTagName("main")

            boxes = []

            for main_element in main_elements:
                # check if the box belongs to the current page
                if not self.belongs_to(main_element, page):
                    continue

                type = main_element.getAttribute("jcr:primaryType")

                # the "epfl:faqBox" element contains one or more "epfl:faqList"
                if "epfl:faqBox" == type:
                    faq_list_elements = main_element.getElementsByTagName("faqList")

                    for faq_list_element in faq_list_elements:
                        box = Box(self, page, faq_list_element, multibox=False)
                        boxes.append(box)

                else:
                    # TODO remove the multibox parameter and check for combo boxes instead
                    # Check if xml_box contains many boxes
                    multibox = main_element.getElementsByTagName("text").length > 1
                    box = Box(self, page, main_element, multibox=multibox)
                    boxes.append(box)

            page.boxes = boxes

    def parse_sidebar(self, dom):
        """Parse the sidebar"""
        extra = dom.getElementsByTagName("extra")

        for element in extra:
            box = Box(self, None, element)
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

    def belongs_to(self, element, page):
        """Check if the given element belongs to the given page"""
        parent = element.parentNode

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

    def __init__(self, site, element):
        self.site = site
        self.pid = element.getAttribute("jahia:pid")
        self.template = element.getAttribute("jahia:template")
        self.title = element.getAttribute("jahia:title")
        self.parent = None
        self.children = []

        # if we have a sitemap we don't want to parse the
        # page and add it to it's parent, so we stop here
        if "sitemap" == self.template:
            return

        if self.is_homepage():
            self.name = "index.html"
        else:
            self.name = slugify(self.title) + ".html"

        # find the parent
        element_parent = element.parentNode

        while "jahia:page" != element_parent.nodeName:
            element_parent = element_parent.parentNode

            # we reached the top of the document
            if not element_parent:
                break

        if element_parent:
            self.parent = self.site.pages_dict[element_parent.getAttribute("jahia:pid")]
            self.parent.children.append(self)

    def __str__(self):
        return self.pid + " " + self.template + " " + self.title

    def is_homepage(self):
        """
        Return True if the page is the homepage
        """
        return self.template == "home"

    def has_children(self):
        """
        Return True if the page has children
        """
        return len(self.children) > 0


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
        "epfl:actuBox": "actu",
        "epfl:faqContainer": "faq"
    }

    def __init__(self, site, page, element, multibox=False):
        self.site = site
        self.page = page
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
        # faq
        elif "faq" == self.type:
            self.set_box_faq(element)

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

    def set_box_faq(self, element):
        """set the attributes of a faq box"""
        self.question = Utils.get_tag_attribute(element, "question", "jahia:value")

        self.answer = Utils.get_tag_attribute(element, "answer", "jahia:value")

        self.content = "<h2>%s</h2><p>%s</p>" % (self.question, self.answer)

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
    domain = DOMAIN
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
