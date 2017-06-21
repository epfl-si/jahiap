"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os
import logging

from abc import ABCMeta, abstractclassmethod


class Node(metaclass=ABCMeta):

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = None
        self.children = []
        if parent is not None:
            if not isinstance(parent, Node):
                raise ValueError("Parent nodes must be instances of Node")
            parent.add_child(self)

    @abstractclassmethod
    def run(self):
        pass

    def full_name(self):
        """ Construct the concatenation of all parents' names """
        pointer = self
        nodes = [self.name]
        while pointer.parent is not None:
            nodes.insert(0, pointer.parent.name)
            pointer = pointer.parent
        return "/".join(nodes)

    def add_child(self, node):
        """ Set both children and parent """
        self.children.append(node)
        node.parent = self
        return self


class RootNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

    def run(self):
        # stop running countainer first (if any)
        os.system("docker rm -f %s" % self.name)

        # run new countainer
        docker_cmd = """docker run -d \
        --name "%(site_name)s" \
        --restart=always \
        --net wp-net \
        --label "traefik.enable=true" \
        --label "traefik.backend=static-%(site_name)s" \
        --label "traefik.frontend=static-%(site_name)s" \
        --label "traefik.frontend.rule=Host:%(WP_HOST)s;PathPrefix:/%(WP_PATH)s/%(site_name)s" \
        -v %(abs_output_dir)s/%(site_name)s/html:/usr/share/nginx/html \
        nginx
        """ % {
            'site_name': self.name,
            'abs_output_dir': abs_output_dir,
            'WP_HOST': WP_HOST,
            'WP_PATH': WP_PATH,
        }
        os.system(docker_cmd)
        logging.info("Docker launched for %s", site_name)


class ListNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

    def run(self):
        pass


class SiteNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

    def run(self):
        pass
