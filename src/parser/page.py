"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
from parser.navigation_page import NavigationPage


class Page:
    """A Jahia Page. Has 1 to N Jahia Boxes"""

    def __init__(self, site, element):
        # common data for all languages
        self.element = element
        self.pid = element.getAttribute("jahia:pid")
        self.uuid = element.getAttribute("jcr:uuid")
        self.site = site
        self.template = element.getAttribute("jahia:template")
        self.parent = None
        self.children = []
        # a list of NavigationPages
        self.navigation = []
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

        # parse the navigation
        self.parse_navigation()

    def is_homepage(self):
        """
        Return True if the page is the homepage
        """
        return self.parent is None

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
            self.parent = self.site.pages_by_pid[element_parent.getAttribute("jahia:pid")]
            self.parent.children.append(self)

            # calculate the page level
            self.level = 1

            parent_page = self.parent

            while not parent_page.is_homepage():
                self.level += 1

                parent_page = parent_page.parent

    def parse_navigation(self):
        """Parse the navigation"""

        navigation_pages = self.element.getElementsByTagName("navigationPage")

        for navigation_page in navigation_pages:
            # check if the <navigationPage> belongs to this page
            if not self.site.belongs_to(element=navigation_page, page=self):
                continue

            for child in navigation_page.childNodes:
                # internal page declared with <jahia:page>
                if child.nodeName == "jahia:page":
                    template = child.getAttribute("jahia:template")

                    # we don't want the sitemap
                    if not template == "sitemap":
                        ref = child.getAttribute("jcr:uuid")
                        title = child.getAttribute("jahia:title")

                        self.add_navigation_page(type="internal", ref=ref, title=title)

                # internal page declared with <jahia:link>
                elif child.nodeName == "jahia:link":
                    ref = child.getAttribute("jahia:reference")
                    title = child.getAttribute("jahia:title")

                    self.add_navigation_page(type="internal", ref=ref, title=title)

                # external page
                elif child.nodeName == "jahia:url":
                    ref = child.getAttribute("jahia:value")
                    title = child.getAttribute("jahia:title")

                    self.add_navigation_page(type="external", ref=ref, title=title)

    def add_navigation_page(self, type, ref, title):
        """Add a NavigationPage with the given info"""

        navigation_page = NavigationPage(parent=self, type=type, ref=ref, title=title)

        self.navigation.append(navigation_page)

    def __str__(self):
        return self.pid + " " + self.template
