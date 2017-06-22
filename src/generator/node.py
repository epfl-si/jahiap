"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os
import logging

from abc import ABCMeta, abstractclassmethod

from generator.utils import Utils


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
    def run(self, args):
        pass

    @abstractclassmethod
    def create_html(self, args):
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

    def set_children(self, nodes):

        children = []
        for current_node in nodes:
            if current_node.name != 'root' and current_node.parent.name == self.name:
                children.append(current_node)

        self.children = children

    def set_parent(self, nodes, name):
        """
        Set parent node
        """
        for node in nodes:
            if node.name == name:
                self.parent = node
                break


class RootNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

    def create_html(self, args):
        # load and render template
        template = self.env.get_template('root.html')
        content = template.render()

        # create file
        with open("index.html", 'w') as output:
            output.write(content)
            output.flush()

    def run(self, args):
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

    def create_html(self, args):
        pass

    def run(self, args):
        pass


class SiteNode(Node):
    def __init__(self, name, parent=None):
        super().__init__(name, parent=parent)

    def create_html(self, args):
        pass

    def run(self, args):
        pass


def create_all_nodes(sites):
    """
    Create all nodes without relationship
    """
    nodes = []

    # Create the root node
    root = RootNode(name="root")
    nodes.append(root)

    # Create the list and site nodes
    for site in sites:
        if site['type'] == 'list':
            node = ListNode(name=site['name'])
        elif site['type'] == 'site':
            node = SiteNode(name=site['name'])
        nodes.append(node)
    return nodes


def set_all_parents(sites, nodes):
    """
    Set the parent for all nodes
    """
    for site in sites:
        for node in nodes:
            if site['name'] == node.name:
                node.set_parent(nodes, name=site['parent'])
                break
    return nodes


def set_all_children(sites, nodes):

    for site in sites:
        for node in nodes:
            if site['name'] == node.name:
                node.set_children(nodes)
                break
    return nodes


def create_the_world(args):
    """
    Create all docker container for all sites
    """

    # parse csv file and get all sites information
    sites = Utils.get_content_of_csv_file(filename="sites.csv")
    sites.append({'name': 'root', 'parent': '', 'type': 'root'})

    # create all nodes without relationship
    nodes = create_all_nodes(sites)

    # set the parent for all nodes
    nodes = set_all_parents(sites, nodes)

    # set children
    nodes = set_all_children(sites, nodes)

    # run all nodes
    for node in nodes:
        node.run(args)
