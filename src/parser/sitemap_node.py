from anytree import Node, RenderTree


class SitemapNode(Node):
    """A SitemapNode"""

    def __init__(self, name, page, parent=None):

        super().__init__(name, parent)

        self.page = page

    def print_node(self):
        """Print the node"""

        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))
