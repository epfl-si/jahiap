from anytree import Node


class SitemapNode(Node):
    """A SitemapNode"""

    def __init__(self, name, page, parent=None):

        super().__init__(name, parent)

        self.page = page
