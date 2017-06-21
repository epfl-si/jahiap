"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
from datetime import datetime

from box import Box
from settings import JAHIA_DATE_FORMAT
from sidebar import Sidebar


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
                    box = Box(site=self.site, page_content=self, element=extra)
                    self.sidebar.boxes.append(box)

        # if not found, search the sidebar of a parent
        # TODO by Greg: Fix the infinite loop
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
                self.path = vanity_url.split('$$$')[0]
            else:
                # use the old Jahia page id
                self.path = "/page-%s-%s.html" % (self.page.pid, self.language)

        # add the site root_path at the beginning
        self.path = self.site.root_path + self.path
