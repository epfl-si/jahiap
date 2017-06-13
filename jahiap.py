"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

import argparse
import logging
import os
import pickle
import tempfile
import xml.dom.minidom
import zipfile

from pprint import pprint, pformat
from datetime import datetime

from exporter.dict_exporter import DictExporter
from exporter.html_exporter import HTMLExporter
from exporter.wp_exporter import WPExporter
from settings import DOMAIN, JAHIA_DATE_FORMAT


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


class Site:
    """A Jahia Site. Have 1 to N Pages"""

    def __init__(self, base_path, name):
        self.base_path = base_path
        self.name = name

        # the export files containing the pages data.
        # the dict key is the language code (e.g. "en") and
        # the dict value is the file absolute path
        self.export_files = {}

        # the site languages
        self.languages = []

        for file in os.listdir(base_path):
            if file.startswith("export_"):
                language = file[7:9]
                path = base_path + "/" + file
                self.export_files[language] = path
                self.languages.append(language)

        # site params that are parsed later. There are dicts because
        # we have a value for each language. The dict key is the language,
        # and the dict value is the specific value
        self.title = {}
        self.acronym = {}
        self.theme = {}
        self.css_url = {}

        # breadcrumb
        self.breadcrumb_title = {}
        self.breadcrumb_url = {}

        # footer
        self.footer = []

        # the pages. We have a both list and a dict.
        # The dict key is the page id, and the dict value is the page itself
        self.pages = []
        self.pages_dict = {}

        # set for convenience, to avoid:
        #   [p for p in self.pages if p.is_homepage()][0]
        self.homepage = None

        # the files
        self.files = []

        # parse the data
        self.parse_data()

        # generate the report
        self.report = ""

        self.generate_report()

    def parse_data(self):
        """Parse the Site data"""

        # do the parsing
        self.parse_site_params()
        self.parse_breadcrumb()
        self.parse_footer()
        self.parse_pages()
        self.parse_pages_content()
        self.parse_files()

    def parse_site_params(self,):
        """Parse the site params"""
        for language, dom_path in self.export_files.items():
            dom = Utils.get_dom(dom_path)

            self.title[language] = Utils.get_tag_attribute(dom, "siteName", "jahia:value")
            self.theme[language] = Utils.get_tag_attribute(dom, "theme", "jahia:value")
            self.acronym[language] = Utils.get_tag_attribute(dom, "acronym", "jahia:value")
            self.css_url[language] = "//static.epfl.ch/v0.23.0/styles/%s-built.css" % self.theme

    def parse_footer(self, dom):
        """parse site footer"""

        # is positioned on children of main jahia:page element
        elements = dom.firstChild.childNodes

        for child in elements:

            if child.ELEMENT_NODE != child.nodeType:
                continue

            if "bottomLinksListList" == child.nodeName:

                nb_items_in_footer = len(child.getElementsByTagName("jahia:url"))

                if nb_items_in_footer == 0:
                    """ This site has the default footer"""
                    break

                elif nb_items_in_footer > 0:

                    elements = child.getElementsByTagName("jahia:url")
                    for element in elements:
                        link = Link(
                            url=element.getAttribute('jahia:value'),
                            title=element.getAttribute('jahia:title')
                        )
                        self.footer.append(link)
                    break

    def parse_breadcrumb(self):
        """Parse the breadcrumb"""

        for language, dom_path in self.export_files.items():
            dom = Utils.get_dom(dom_path)

            breadcrumb_link = dom.getElementsByTagName("breadCrumbLink")[0]

            for child in breadcrumb_link.childNodes:
                if child.ELEMENT_NODE != child.nodeType:
                    continue

                if 'jahia:url' == child.nodeName:
                    self.breadcrumb_url[language] = child.getAttribute('jahia:value')
                    self.breadcrumb_title[language] = child.getAttribute('jahia:title')
                    break

    def parse_pages(self):
        """
        Parse the Pages. Here we parse only the common data between
        multilingual pages
        """

        # we check each export files because a Page could be defined
        # in one language but not in another
        for language, dom_path in self.export_files.items():
            dom = Utils.get_dom(dom_path)

            xml_pages = dom.getElementsByTagName("jahia:page")

            for xml_page in xml_pages:
                pid = xml_page.getAttribute("jahia:pid")
                template = xml_page.getAttribute("jahia:template")

                # we don't parse the sitemap as it's not a real page
                if template == "sitemap":
                    continue

                # check if we already parsed this page
                if pid in self.pages_dict:
                    continue

                page = Page(self, xml_page)

                # flag the homepage for convenience
                if page.is_homepage():
                    self.homepage = page

                # add the Page to the Site
                self.pages.append(page)
                self.pages_dict[page.pid] = page

    def parse_pages_content(self):
        """
        Parse the PageContent. This is the content that is specific
        for each language.
        """

        for language, dom_path in self.export_files.items():
            dom = Utils.get_dom(dom_path)

            xml_pages = dom.getElementsByTagName("jahia:page")

            for xml_page in xml_pages:
                pid = xml_page.getAttribute("jahia:pid")
                template = xml_page.getAttribute("jahia:template")

                # we don't parse the sitemap as it's not a real page
                if template == "sitemap":
                    continue

                # retrieve the Page definition that we already parsed
                page = self.pages_dict[pid]
                page_content = PageContent(page, language, xml_page)

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
                            box = Box(site=self, page_content=page_content, element=faq_list_element)
                            boxes.append(box)

                    else:
                        # TODO remove the multibox parameter and check for combo boxes instead
                        # Check if xml_box contains many boxes
                        multibox = main_element.getElementsByTagName("text").length > 1
                        box = Box(site=self, page_content=page_content, element=main_element, multibox=multibox)
                        boxes.append(box)

                page_content.boxes = boxes
                page.contents[language] = page_content

    def parse_files(self):
        """Parse the files"""
        start = "%s/content/sites/%s/files" % (self.base_path, self.name)

        for (path, dirs, files) in os.walk(start):
            for file_name in files:
                # we exclude the thumbnails
                if file_name in ["thumbnail", "thumbnail2"]:
                    continue

                self.files.append(File(name=file_name, path=path))

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
            for page_content in page.contents.values():
                for box in page_content.boxes:
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

    def __init__(self):
        self.boxes = []


class Page:
    """A Jahia Page. Has 1 to N Jahia Boxes"""

    def __init__(self, site, element):
        # common data for all languages
        self.pid = element.getAttribute("jahia:pid")
        self.site = site
        self.template = element.getAttribute("jahia:template")
        self.parent = None
        self.children = []
        # the page level. 0 is for the homepage, direct children are
        # at level 1, grandchildren at level 2, etc.
        self.level = 0

        # the PageContents, one for each language. The dict key is the
        # language, the dict value is the PageContent
        self.contents = {}

        # if we have a sitemap we don't want to parse the
        # page and add it to it's parent, so we stop here
        if "sitemap" == self.template:
            return

        # find the Page parent
        self.set_parent(element)

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

    def set_parent(self, element):
        """
        Find the page parent
        """
        element_parent = element.parentNode

        while "jahia:page" != element_parent.nodeName:
            element_parent = element_parent.parentNode

            # we reached the top of the document
            if not element_parent:
                break

        if element_parent:
            self.parent = self.site.pages_dict[element_parent.getAttribute("jahia:pid")]
            self.parent.children.append(self)

            # calculate the page level
            self.level = 1

            parent_page = self.parent

            while not parent_page.is_homepage():
                self.level += 1

                parent_page = parent_page.parent

    def __str__(self):
        return self.pid + " " + self.template


class PageContent:
    """
    The language specific data of a Page
    """
    def __init__(self, page, language, element):
        self.page = page
        self.language = language
        # the relative path, e.g. /team.html
        self.path = ""
        self.title = element.getAttribute("jahia:title")
        self.boxes = []
        self.sidebar = Sidebar()
        self.last_update = datetime.strptime(
            element.getAttribute("jcr:lastModified"),
            JAHIA_DATE_FORMAT)

        # sidebar
        self.parse_sidebar(element)

        # path
        self.set_path(element)

    def parse_sidebar(self, element):
        """ Parse sidebar """

        # search the sidebar in the page xml content
        children = element.childNodes
        for child in children:
            if child.nodeName == "extraList":
                for extra in child.childNodes:
                    if extra.ELEMENT_NODE != extra.nodeType:
                        continue
                    box = Box(site=self.page.site, page_content=self, element=element, multibox=extra)
                    self.sidebar.boxes.append(box)

        # if not found, search the sidebar of a parent
        nb_boxes = len(self.sidebar.boxes)
        if nb_boxes == 0:
            while nb_boxes == 0:
                sidebar = self.page.parent.contents[self.language].sidebar
                nb_boxes = len(sidebar.boxes)
            self.sidebar = sidebar

    def set_path(self, element):
        """
        Set the page path
        """

        if self.page.is_homepage():
            if "en" == self.language:
                self.path = "/index.html"
            else:
                self.path = "/index-%s.html" % self.language
        else:
            vanity_url = element.getAttribute("jahia:urlMappings")
            if vanity_url:
                self.path = vanity_url.split('$$$')[0] + ".html"
            else:
                self.path = self.regular_path()

    def regular_path(self):
        return "/page-%s-%s.html" % (self.page.pid, self.language)


class Box:
    """A Jahia Box. Can be of type text, infoscience, etc."""

    # the known box types
    types = {
        "epfl:textBox": "text",
        "epfl:coloredTextBox": "coloredText",
        "epfl:infoscienceBox": "infoscience",
        "epfl:actuBox": "actu",
        "epfl:faqContainer": "faq",
        "epfl:toggleBox": "toggle"
    }

    def __init__(self, site, page_content, element, multibox=False):
        self.site = site
        self.page_content = page_content
        self.set_type(element)
        self.title = Utils.get_tag_attribute(element, "boxTitle", "jahia:value")
        self.content = ""
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
        # toggle
        elif "toggle" == self.type:
            self.set_box_toggle(element)

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

    def set_box_toggle(self, element):
        """set the attributes of a toggle box"""
        self.opened = Utils.get_tag_attribute(element, "opened", "jahia:value")

        self.content = Utils.get_tag_attribute(element, "content", "jahia:value")

    def __str__(self):
        return self.type + " " + self.title


class File:
    """A Jahia File"""

    def __init__(self, name, path):
        self.name = name
        self.path = path


def main(parser, args):
    """
        Setup context (e.g debug level) and forward to command-dedicated main function
    """
    logging.info("Starting jahiap script...")

    # mkdir from output_dir or as temporary dir
    if args.output_dir:
        if not os.path.isdir(args.output_dir):
            os.mkdir(args.output_dir)
    else:
        args.output_dir = tempfile.mkdtemp()
        logging.warning("Created temporary directory %s, please remove it when done" % args.output_dir)

    # forward to appropriate main function
    args.command(parser, args)


def main_unzip(parser, args):
    logging.info("Unzipping %s..." % args.zip_file)

    # make sure we have an input file
    if not args.zip_file or not os.path.isfile(args.zip_file):
        parser.print_help()
        raise SystemExit("Jahia zip file not found")

    # create zipFile to manipulate / extract zip content
    export_zip = zipfile.ZipFile(args.zip_file, 'r')

    # find the zip containing the site files
    zips = [name for name in export_zip.namelist() if name.endswith(".zip") and name != "shared.zip"]
    if len(zips) != 1:
        logging.error("Should have one and only one zip file in %s" % zips)
        raise SystemExit("Could not find appropriate zip with files")
    zip_with_files = zips[0]

    # extract the export zip file
    export_zip.extractall(args.output_dir)
    export_zip.close()

    # get the site name
    site_name = zip_with_files[:zip_with_files.index(".")]

    base_path = os.path.join(args.output_dir, site_name)

    # unzip the zip with the files
    zip_path = os.path.join(args.output_dir, zip_with_files)
    zip_ref_with_files = zipfile.ZipFile(zip_path, 'r')
    zip_ref_with_files.extractall(base_path)

    # return site path & name
    logging.info("Site successfully extracted in %s" % base_path)
    return (base_path, site_name)


def main_parse(parser, args):
    logging.info("Parsing...")

    base_path = os.path.join(args.output_dir, args.site_name)

    site = Site(base_path, args.site_name)

    if args.print_report:
        print(site.report)

    # save parsed site on file system
    file_name = os.path.join(
        args.output_dir,
        'parsed_%s.pkl' % args.site_name)

    with open(file_name, 'wb') as output:
        pickle.dump(site, output, pickle.HIGHEST_PROTOCOL)

    # return site object
    logging.info("Site successfully parsed, and saved into %s" % file_name)
    return site


def main_export(parser, args):
    # restore parsed site from file system
    file_name = os.path.join(
        args.output_dir,
        'parsed_%s.pkl' % args.site_name)
    if os.path.exists(file_name):
        with open(file_name, 'rb') as input:
            site = pickle.load(input)
        logging.info("Loaded parsed site from %s" % file_name)
    # or parse it again
    else:
        args.print_report = False
        site = main_parse(parser, args)

    logging.info("Exporting...")

    if args.to_wordpress:
        wp_exporter = WPExporter(site=site, domain=args.site_url)
        wp_exporter.import_all_data_in_wordpress()
        logging.info("Site successfully exported to Wordpress")

    if args.to_static:
        export_path = os.path.join(
            args.output_dir, "%s_html" % args.site_name)
        HTMLExporter(site, export_path)
        logging.info("Site successfully exported to HTML files")

    if args.to_dictionary:
        export_path = os.path.join(
            args.output_dir, "%s_dict.py" % args.site_name)
        data = DictExporter.generate_data(site)
        pprint(data)
        with open(export_path, 'w') as output:
            output.write("%s_data = " % args.site_name)
            output.write(pformat(data))
            output.flush()
        logging.info("Site successfully exported to python dictionary")


if __name__ == '__main__':
    # declare parsers for command line arguments
    parser = argparse.ArgumentParser(
        description='Unzip, parse and export Jahia XML')
    subparsers = parser.add_subparsers()

    # logging-related agruments
    parser.add_argument('--debug',
                        dest='debug',
                        action='store_true',
                        help='Set logging level to DEBUG (default is INFO)')
    parser.add_argument('--quiet',
                        dest='quiet',
                        action='store_true',
                        help='Set logging level to WARNING (default is INFO)')

    # common arguments for all commands
    parser.add_argument('-o', '--output-dir',
                        dest='output_dir',
                        help='directory where to unzip, parse, export Jahia XML')

    # "unzip" command
    parser_unzip = subparsers.add_parser('unzip')
    parser_unzip.add_argument('zip_file', help='path to Jahia XML file')
    parser_unzip.set_defaults(command=main_unzip)

    # "parse" command
    parser_parse = subparsers.add_parser('parse')
    parser_parse.add_argument(
        'site_name',
        help='name of sub directories that contain the site files')
    parser_parse.add_argument(
        '-r', '--print-report',
        dest='print_report',
        action='store_true',
        help='print report with parsed content')
    parser_parse.set_defaults(command=main_parse)

    # "export" command
    parser_export = subparsers.add_parser('export')
    parser_export.add_argument(
        'site_name',
        help='name of sub directories that contain the site files')
    parser_export.add_argument(
        '-w', '--to-wordpress',
        dest='to_wordpress',
        action='store_true',
        help='export parsed data to Wordpress')
    parser_export.add_argument(
        '-s', '--to-static',
        dest='to_static',
        action='store_true',
        help='export parsed data to static HTML files')
    parser_export.add_argument(
        '-d', '--to-dictionary',
        dest='to_dictionary',
        action='store_true',
        help='export parsed data to python dictionary')
    parser_export.add_argument(
        '-u', '--site-url',
        dest='site_url',
        metavar='URL',
        default=DOMAIN,
        help='wordpress URL where to export parsed content')
    parser_export.set_defaults(command=main_export)

    # forward to main function
    args = parser.parse_args()

    # set logging config before anything else
    if args.quiet:
        logging.basicConfig(level=logging.WARNING)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main(parser, args)
