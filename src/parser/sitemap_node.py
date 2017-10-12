from anytree import Node, RenderTree


class SitemapNode(Node):
    """A SitemapNode"""

    def __init__(self, name, page, ref, parent=None):
        super().__init__(name, parent)

        self.page = page
        self.ref = ref

    def print_node(self):
        """Print the node"""

        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))

    @classmethod
    def from_navigation_page(cls, navigation_page, parent):

        return SitemapNode(
            name=navigation_page.title,
            page=navigation_page.page,
            ref=navigation_page.ref,
            parent=parent)
