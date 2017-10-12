"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""


class NavigationPage:
    """A NavigationPage. Can be internal or external"""

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
