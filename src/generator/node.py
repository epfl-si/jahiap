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


class Node():

    env = Environment(
        loader=PackageLoader('generator', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    def __init__(self, name, type_class=None, tree=None):
        self.name = name
        self.tree = tree
        self.__parent = None
        self.__children = []

        # make sure appropiate type is passed
        type_class = type_class or NoTypeNode
        if not issubclass(type_class, TypeNode):
            raise ValueError("Type should be a subclass of TypeNode")
        self.current_type = type_class(self)

        # make sure output_path exists
        if tree and not os.path.exists(self.output_path()):
            os.makedirs(self.output_path())

    def __repr__(self):
        return "<%s %s>" % (self.current_type.__class__.__name__, self.name)

    @property
    def children(self):
        return self.__children

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, parent_node):
        self.__parent = parent_node
        parent_node.__children.append(self)

    def full_name(self):
        return self.current_type.full_name()

    def output_path(self, file_path=""):
        return self.current_type.output_path()

    def absolute_path_to_html(self):
        return self.current_type.absolute_path_to_html()

    def create_html(self):
        return self.current_type.create_html()

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
        --label "traefik.frontend.rule=Host:%(WP_HOST)s;PathPrefix:/%(full_name)s" \
        -v %(absolute_path_to_html)s:/usr/share/nginx/html/%(full_name)s \
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


class TypeNode(metaclass=ABCMeta):

    def __init__(self, node):
        self.node = node

    @abstractclassmethod
    def create_html(self):
        raise NotImplementedError()

    @classmethod
    def get_subclass_from_string(cls, type_name):
        classes = dict([(class_obj.__name__, class_obj) for class_obj in cls.__subclasses__()])
        return classes[type_name]

    def full_name(self):
        """ Construct the concatenation of all parents' names """
        nodes = [self.node.name]
        parent = self.node.parent

        # loop  through all parents, but ignoring tree.root :
        # we do not want the rootname in the full_name
        while parent != self.node.tree.root:
            nodes.insert(0, parent.name)
            parent = parent.parent

        # return a relative fullname, i.e without the first '/'
        return "/".join(nodes)

    def output_path(self, file_path=""):
        dir_path = os.path.join(self.node.tree.output_path, self.node.name)
        return os.path.join(dir_path, file_path)

    def absolute_path_to_html(self):
        return os.path.abspath(self.output_path())


class NoTypeNode(TypeNode):

    def create_html(self):
        raise NotImplementedError()


class RootTypeNode(TypeNode):

    def full_name(self):
        """ Construct the concatenation of all parents' names """
        return ""

    def output_path(self, file_path=""):
        return os.path.join(self.node.tree.output_path, file_path)

    def create_html(self):
        # load and render template
        template = self.node.env.get_template('root.html')
        children_list = dict([(child.name, child.full_name()) for child in self.node.children])
        content = template.render(children_list=children_list)

        # create file
        file_path = self.output_path("index.html")
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()


class ListTypeNode(TypeNode):

    def create_html(self):

        template = self.node.env.get_template('list.html')
        children_list = dict([(child.name, child.full_name()) for child in self.node.children])
        content = template.render(name=self.node.name, children_list=children_list)

        # create file
        file_path = self.output_path("index.html")
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()


class SiteTypeNode(TypeNode):

    def absolute_path_to_html(self):
        return os.path.join(
            os.path.abspath(self.output_path()),
            self.node.full_name())

    def create_html(self):
        zip_file = SiteCrawler(self.node.name, self.node.tree.args).download_site()
        site_dir = unzip_one(self.node.tree.args['--output-dir'], self.node.name, zip_file)
        site = Site(site_dir, self.node.name, root_path=self.node.full_name())
        HTMLExporter(site, self.output_path())
