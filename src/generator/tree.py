"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

from generator.node import Node, RootNode


class Tree:

    def __init__(self, args, sites):

        self.args = args
        self.sites = sites
        self.output_path = os.path.join(
            args.get('--output-dir', '.'),
            "generator")

        # create root
        self.root = RootNode(name="root", tree=self)
        self.nodes = {self.root.name: self.root}

        # create all nodes
        for site in sites:
            node = Node.factory(name=site['name'], type=site['type'], data=site, tree=self)
            self.nodes[node.name] = node

        # create all relation
        for site in self.sites:
            node = self.nodes[site['name']]
            parent = self.nodes[site['parent']]
            node.parent = parent

    def __repr__(self):
        return "<Tree root=%s #nodes=%s path=%s>" \
               % (self.root.name, len(self.nodes), self.output_path)

    def prepare_run(self):
        """
        Generate HTML files for all nodes
        """
        for node in self.nodes.values():
            node.prepare_run()

    def run(self):
        """
        Create all docker container for all sites
        """
        for node in self.nodes.values():
            node.run()
