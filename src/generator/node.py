"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import logging
import os
from abc import ABCMeta, abstractclassmethod

from jinja2 import Environment, PackageLoader, select_autoescape

from crawler import SiteCrawler
from unzipper.unzip import unzip_one
from exporter.html_exporter import HTMLExporter
from jahia_site import Site
from generator.utils import Utils
from settings import WP_HOST, PROJECT_PATH


class Node(metaclass=ABCMeta):

    env = Environment(
        loader=PackageLoader('generator', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    def __init__(self, name, tree=None):
        self.name = name
        self.tree = tree
        self.parent = None
        self.children = []

        # make sure output_path exists
        if tree and not os.path.exists(self.output_path()):
            os.makedirs(self.output_path())

    @abstractclassmethod
    def create_html(self):
        raise NotImplementedError()

    def run(self):

        # stop running container first (if any)
        os.system("docker rm -f generated-%s" % self.name)

        # run new countainer
        docker_cmd = """docker run -d \
        --name "generated-%(site_name)s" \
        --restart=always \
        --net wp-net \
        --label "traefik.enable=true" \
        --label "traefik.backend=generated-%(site_name)s" \
        --label "traefik.frontend=generated-%(site_name)s" \
        --label "traefik.frontend.rule=Host:%(WP_HOST)s;PathPrefix:%(full_name)s" \
        -v %(absolute_path_to_html)s:/usr/share/nginx/html%(full_name)s \
        -v %(absolute_project_path)s/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
        nginx
        """ % {
            'site_name': self.name,
            'absolute_path_to_html': self.absolute_path_to_html(),
            'absolute_project_path': PROJECT_PATH,
            'full_name': self.full_name(),
            'WP_HOST': WP_HOST,
        }
        os.system(docker_cmd)
        logging.debug(docker_cmd)
        logging.info("Docker launched for %s", self.name)

    def output_path(self, file_path=""):
        dir_path = os.path.join(self.tree.output_path, self.name)
        return os.path.join(dir_path, file_path)

    def absolute_path_to_html(self):
        return os.path.abspath(self.output_path())

    def full_name(self, relative=False):
        """ Construct the concatenation of all parents' names """
        nodes = [self.name]
        parent = self.parent
        while parent is not None:
            nodes.insert(0, parent.name)
            parent = parent.parent
        # getting the RootNode out of the way if relative
        if relative:
            return "/".join(nodes).strip('/')
        return "/".join(nodes)

    def set_children(self, nodes):

        children = []
        for current_node in nodes:
            if current_node.parent and current_node.parent.name == self.name:
                children.append(current_node)

        self.children = children

    def set_parent(self, nodes, name):
        """
        Set parent node
        """
        for node in nodes:
            if node.name == '' and name == 'root':
                self.parent = node
            elif node.name == name:
                self.parent = node
                break


class RootNode(Node):
    def __init__(self, name, tree=None):
        super().__init__(name, tree=tree)

    def full_name(self, relative=False):
        if relative:
            self.name
        return "/" + self.name

    def create_html(self):
        # load and render template
        template = self.env.get_template('root.html')
        children_list = dict([(child.name, child.full_name()) for child in self.children])
        content = template.render(children_list=children_list)

        # create file
        file_path = self.output_path("index.html")
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()


class ListNode(Node):

    def __init__(self, name, tree=None):
        super().__init__(name, tree=tree)

    def create_html(self):

        template = self.env.get_template('list.html')
        children_list = dict([(child.name, child.full_name()) for child in self.children])
        content = template.render(name=self.name, children_list=children_list)

        # create file
        file_path = self.output_path("index.html")
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()


class SiteNode(Node):
    def __init__(self, name, tree=None):
        super().__init__(name, tree=tree)

    def absolute_path_to_html(self):
        return os.path.join(os.path.abspath(self.output_path()), self.full_name(relative=True))

    def create_html(self):
        zip_file = SiteCrawler(self.name, self.tree.args).download_site()
        site_dir = unzip_one(self.tree.args['--output-dir'], self.name, zip_file)
        site = Site(site_dir, self.name, root_path=self.full_name())
        HTMLExporter(site, self.output_path())


class Tree(object):

    def __init__(self, args, filename="sites.csv"):
        self.root = None
        self.args = args
        self.output_path = os.path.join(args['--output-dir'], "generator")

        # parse csv file and get all sites information
        sites = Utils.get_content_of_csv_file(filename=filename)
        sites.append({'name': '', 'parent': '', 'type': 'root'})

        # create all nodes without relationship
        nodes = self.create_all_nodes(sites)

        # set the parent for all nodes
        nodes = self.set_all_parents(sites, nodes)

        # set children
        self.nodes = self.set_all_children(sites, nodes)

    def create_all_nodes(self, sites):
        """
        Create all nodes without relationship
        """
        nodes = []

        # Create the list and site nodes
        # TODO: replace by factory ?
        for site in sites:
            if site['type'] == 'list':
                node = ListNode(name=site['name'], tree=self)
            elif site['type'] == 'site':
                node = SiteNode(name=site['name'], tree=self)
            elif site['type'] == 'root':
                node = RootNode(name="", tree=self)
                self.root = node
            else:
                logging.error("unsupported type")
            nodes.append(node)
        return nodes

    @staticmethod
    def set_all_parents(sites, nodes):
        """
        Set the parent for all nodes
        """
        for site in sites:
            for node in nodes:
                if node.name != '' and site['name'] == node.name:
                    node.set_parent(nodes, name=site['parent'])
                    break
        return nodes

    @staticmethod
    def set_all_children(sites, nodes):

        for site in sites:
            for node in nodes:
                if site['name'] == node.name:
                    node.set_children(nodes)
                    break
        return nodes

    def create_html(self):
        """
        Generate HTML files for all nodes
        """
        for node in self.nodes:
            node.create_html()

    def run(self):
        """
        Create all docker container for all sites
        """
        for node in self.nodes:
            node.run()
