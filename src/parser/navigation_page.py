"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""


class NavigationPage:
    """
    A NavigationPage is a reference to another page. It can be internal (another Jahia Page),
    or external (a URL, e.g. https://www.google.com). It is used to determine which pages
    are directly below another one, so it's used by the sitemap and the navigation.

    You will probably not want to use this class directly and instead use a SitemapNode
    available as site.sitemaps["en"].
    """

    def __init__(self, parent, type, ref, title):
        self.parent = parent
        self.type = type
        self.ref = ref
        self.title = title

    @property
    def page(self):
        if self.ref in self.parent.site.pages_by_uuid:
            return self.parent.site.pages_by_uuid[self.ref]
        else:
            return None

    def __str__(self):
        return self.type + " " + self.ref + " " + self.title
