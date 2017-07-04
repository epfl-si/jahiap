"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import logging
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException

from crawler import SiteCrawler
from parser.jahia_site import Site
from unzipper.unzip import unzip_one
from exporter.html_exporter import HTMLExporter
from settings import WP_HOST, PROJECT_PATH
from generator.utils import Utils as UtilsGenerator


class Node:

    env = Environment(
        loader=PackageLoader('generator', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    def __init__(self, name, data=None, tree=None):
        self.name = name
        self.data = data
        self.tree = tree
        self.__parent = None
        self.__children = []

        # make sure output_path exists
        if tree and not os.path.exists(self.output_path()):
            os.makedirs(self.output_path())

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.name)

    @staticmethod
    def factory(name, type, data, tree):
        if type == "RootNode":
            return RootNode(name, data, tree)
        if type == "ListNode":
            return ListNode(name, data, tree)
        if type == "SiteNode":
            return SiteNode(name, data, tree)
        if type == "WordPressNode":
            return WordPressNode(name, data, tree)
        raise Exception("Unknown node type")

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
        """ Construct the concatenation of all parents' names """
        nodes = [self.name]
        parent = self.parent

        # loop  through all parents, but ignoring tree.root :
        # we do not want the rootname in the full_name
        while parent != self.tree.root:
            nodes.insert(0, parent.name)
            parent = parent.parent

        # return a relative fullname, i.e without the first '/'
        return "/".join(nodes)

    def output_path(self, file_path=""):
        dir_path = os.path.join(self.tree.output_path, self.name)
        return os.path.join(dir_path, file_path)

    def absolute_path_to_html(self):
        return os.path.abspath(self.output_path())

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

    def cleanup(self):
        docker_cmd = 'docker rm -f generated-%s' % self.name
        os.system(docker_cmd)
        logging.debug(docker_cmd)
        logging.info("Docker '%s' stopped and removed", self.name)


class RootNode(Node):

    def full_name(self):
        """ Construct the concatenation of all parents' names """
        return ""

    def output_path(self, file_path=""):
        return os.path.join(self.tree.output_path, file_path)

    def prepare_run(self):
        """
        In this case we create only a index.html file with the children links.
        """
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

    def prepare_run(self):
        """
        In this case we create only a index.html file with the children links.
        """

        template = self.env.get_template('list.html')
        children_list = dict([(child.name, child.full_name()) for child in self.children])
        content = template.render(name=self.name, children_list=children_list)

        # create file
        file_path = self.output_path("index.html")
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()


class SiteNode(Node):

    def absolute_path_to_html(self):
        return os.path.join(
            os.path.abspath(self.output_path()),
            self.full_name())

    def prepare_run(self):
        zip_file = SiteCrawler(self.name, self.tree.args).download_site()
        site_dir = unzip_one(self.tree.args['--output-dir'], self.name, zip_file)
        site = Site(site_dir, self.name, root_path="/"+self.full_name())
        HTMLExporter(site, self.output_path())


class WordPressNode(Node):

    def absolute_path_to_html(self):
        return os.path.join(
            os.path.abspath(self.output_path()),
            self.full_name())

    def prepare_yaml(self, conf_path):
        # build yml file
        template = self.env.get_template('conf.yaml')
        content = template.render(wp_host=WP_HOST, full_name=self.full_name(), **self.data)

        # build file path
        parent = self.parent
        if parent == 'root':
            dir_path = conf_path
        else:
            dir_path = os.path.join(conf_path, parent.full_name())
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        file_path = os.path.join(dir_path, self.name) + ".yaml"

        # write yml file
        with open(file_path, 'w') as output:
            output.write(content)
            output.flush()
            logging.info("(ok) %s", file_path)

        return file_path

    def prepare_composition(self, args, yaml_path):
        """
            Create project from the template. See API reference online:
            https://cookiecutter.readthedocs.io/en/latest/cookiecutter.html#module-cookiecutter.main
        """
        logging.info("Starting cookiecutter...")
        try:
            site_path = cookiecutter(
                args['--cookie-path'],
                no_input=True,
                overwrite_if_exists=args['--force'],
                config_file=yaml_path,
                output_dir=args['--output-dir'])
            logging.info("Site generated into %s", site_path)
            return site_path
        except OutputDirExistsException:
            logging.warning("%s already exists. Use --force to override", yaml_path)

    def prepare_run(self):
        yaml_path = self.prepare_yaml(self.tree.args['--conf-path'])
        self.prepare_composition(self.tree.args, yaml_path)

    def run(self):
        composition_path = os.path.join(self.tree.args['--output-dir'], self.name)
        UtilsGenerator.docker(composition_path, up=True)

    def cleanup(self):
        composition_path = os.path.join(self.tree.args['--output-dir'], self.name)
        UtilsGenerator.docker(composition_path, up=False)
