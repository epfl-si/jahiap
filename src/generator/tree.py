import logging
import os

from generator.utils import Utils
from generator.node import Node, TypeNode, NoTypeNode, RootTypeNode


class Tree(object):

    def __init__(self, args, root_name="root", file_path=None):
        self.args = args
        self.output_path = os.path.join(
            args.get('--output-dir', '.'),
            "generator")

        self.root = Node(name=root_name, type_class=RootTypeNode, tree=self)
        self.nodes = {self.root.name: self.root}

        # parse CSV file and create nodes accordingly
        if file_path:
            self.__create_all_nodes(file_path)

    def __repr__(self):
        return "<Tree root=%s #nodes=%s path=%s>" \
            % (self.root.name, len(self.nodes), self.output_path)

    def __create_all_nodes(self, file_path):
        """
        Create all nodes from CSV file
        """
        logging.debug("loading tree from %s", file_path)

        # check input
        if not os.path.isfile(file_path):
            raise ValueError("given file for Tree does not exist")

        # parse all csv up front
        sites = Utils.get_content_of_csv_file(file_path=file_path)

        # create all nodes
        for (site_name, parent_name, type_name) in sites:
            node = self.get_or_create(site_name, parent_name, type_name)
            logging.debug("created node %s", node)

    def get_or_create(self, name, parent_name=None, type_name="NoTypeNode"):
        # get subclass fir given type name
        type_class = TypeNode.get_subclass_from_string(type_name)

        # check if node with given name exists or create it if with does not exist
        node = self.nodes.setdefault(name, Node(name, type_class=type_class, tree=self))

        # update type if necessary
        if type_class is not NoTypeNode:
            node.current_type = type_class(node)

        # set parent if given
        if parent_name is not None:
            parent_node = self.get_or_create(name=parent_name)
            node.parent = parent_node

        return node

    def create_html(self):
        """
        Generate HTML files for all nodes
        """
        for node in self.nodes.values():
            node.create_html()

    def run(self):
        """
        Create all docker container for all sites
        """
        for node in self.nodes.values():
            node.run()
