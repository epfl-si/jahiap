"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
from datetime import datetime

from box import Box
from settings import JAHIA_DATE_FORMAT
from sidebar import Sidebar
import logging


class PageContent:
    """
    The language specific data of a Page
    """
    def __init__(self, page, language, element):
        self.page = page
        self.site = page.site
        self.language = language
        # the relative path, e.g. /team.html
        self.path = ""
        self.title = element.getAttribute("jahia:title")
        self.boxes = []
        self.sidebar = Sidebar()
        self.last_update = ""

        # last update
        self.parse_last_update(element)

        # sidebar
        self.parse_sidebar(element)

        # path
        self.set_path(element)

        # add to the site PageContents
        self.site.pages_content_by_path[self.path] = self

    def parse_last_update(self, element):
        """Parse the last update information"""
        date = element.getAttribute("jcr:lastModified")

        try:
            self.last_update = datetime.strptime(
                date,
                JAHIA_DATE_FORMAT)
        except ValueError:
            logging.error("Invalid last update date for page %s : %s" % (self.page.pid, date))

    def parse_sidebar(self, element):
        """ Parse sidebar """

        # search the sidebar in the page xml content
        children = element.childNodes
        for child in children:
            if child.nodeName == "extraList":
                for extra in child.childNodes:
                    if extra.ELEMENT_NODE != extra.nodeType:
                        continue
                    box = Box(site=self.site, page_content=self, element=extra)
                    self.sidebar.boxes.append(box)

        nb_boxes = len(self.sidebar.boxes)

        # if we don't have boxes in this sidebar we check the parents
        if nb_boxes == 0:
            parent = self.page.parent

            while parent:
                sidebar = parent.contents[self.language].sidebar

                # we found a sidebar with boxes, we stop
                if len(sidebar.boxes) > 0:
                    self.sidebar = sidebar
                    break

                # otherwise we continue in the hierarchy
                parent = parent.parent

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
                self.path = vanity_url.split('$$$')[0]
            else:
                # use the old Jahia page id
                self.path = "/page-%s-%s.html" % (self.page.pid, self.language)

        # FIXME, the prefixing part should be done in exporter
        # add the site root_path at the beginning
        self.path = self.site.root_path + self.path
