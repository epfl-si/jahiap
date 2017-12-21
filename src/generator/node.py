"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import logging
import os
import time
import timeit
from datetime import timedelta
from jinja2 import Environment, PackageLoader, select_autoescape
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException
import shutil

from crawler import SiteCrawler
from parser.jahia_site import Site
from unzipper.unzip import unzip_one
from exporter.html_exporter import HTMLExporter
from exporter.wp_exporter import WPExporter
from settings import WP_HOST, PROJECT_PATH, MAX_WORDPRESS_STARTING_TIME, \
    MYSQL_ROOT_USER, WP_SUPERADMIN_EMAIL, MYSQL_ROOT_PASSWORD, WP_SUPERADMIN_USER, WP_SUPERADMIN_PASSWORD
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
        self.container_name = "container-%s" % name
        self.db_name = None
        self.__parent = None
        self.__children = []

        # data given for WordPress sites -> set container_name accordingly
        if data is not None:
            self.container_name = self.data.get("container_name", "wp-%s" % name)
            self.db_name = self.data.get("db_name")

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
        os.system("docker rm -f %s" % self.container_name)

        # run new countainer
        docker_cmd = """docker run -d \
        --name "%(container_name)s" \
        --restart=always \
        --net wp-net \
        --label "traefik.enable=true" \
        --label "traefik.backend=%(container_name)s" \
        --label "traefik.frontend=%(container_name)s" \
        --label "traefik.frontend.rule=Host:%(WP_HOST)s;PathPrefix:/%(full_name)s" \
        -v %(absolute_path_to_html)s:/usr/share/nginx/html/%(full_name)s \
        -v %(absolute_project_path)s/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
        nginx
        """ % {
            'container_name': self.container_name,
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
        docker_cmd = 'docker rm -f %s' % self.container_name
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
        # FIXME : Replace dict by OrderedDict
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

    @classmethod
    def get_composition_dir(cls, args):
        return os.path.join(args['--output-dir'], 'compositions')

    def absolute_path_to_html(self):
        return os.path.join(
            os.path.abspath(self.output_path()),
            self.full_name())

    def prepare_yaml(self, conf_path):
        # build yml file
        template = self.env.get_template('conf.yaml')
        content = template.render(
            wp_host=WP_HOST,
            mysql_root_user=MYSQL_ROOT_USER,
            mysql_root_password=MYSQL_ROOT_PASSWORD,
            username_superadmin=WP_SUPERADMIN_USER,
            email_superadmin=WP_SUPERADMIN_EMAIL,
            pwd_superadmin=WP_SUPERADMIN_PASSWORD,
            full_name=self.full_name(),
            **self.data)

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
                output_dir=self.get_composition_dir(args))
            logging.info("Site generated into %s", site_path)
            return site_path
        except OutputDirExistsException:
            logging.warning("%s already exists. Use --force to override", yaml_path)

    def prepare_run(self):
        yaml_path = self.prepare_yaml(self.tree.args['--conf-path'])
        self.prepare_composition(self.tree.args, yaml_path)

    def run(self):
        # built up Wordpress URL and composition_path
        wp_url = "%s/%s" % (WP_HOST, self.full_name())
        composition_path = os.path.join(self.get_composition_dir(self.tree.args), self.container_name)

        # check if site already running
        if UtilsGenerator.is_apache_up(wp_url):
            if not self.tree.args['--force']:
                logging.warning("Apache is already running on %s. Use --force to restart it", wp_url)
                return
            else:
                logging.info("Apache is already running on %s. Stopping container...", wp_url)
                UtilsGenerator.docker(composition_path, up=False)

        # start container & set timer limit the waiting time
        UtilsGenerator.docker(composition_path, up=True)
        start_time = timeit.default_timer()

        # wait fot Apache to start
        while not UtilsGenerator.is_apache_up(wp_url):
            # give more time to apache to start
            time.sleep(10)
            # check execution time
            elapsed = timedelta(seconds=timeit.default_timer() - start_time)
            if elapsed > MAX_WORDPRESS_STARTING_TIME:
                break

        # do export
        if UtilsGenerator.is_apache_up(wp_url):
            # FIXME : do not pass args in Objects
            self.tree.args['--site-path'] = self.full_name()
            self.tree.args['--wp-cli'] = self.container_name
            try:
                zip_file = SiteCrawler(self.name, self.tree.args).download_site()
                site_dir = unzip_one(self.tree.args['--output-dir'], self.name, zip_file)
                site = Site(site_dir, self.name)
                wp_exporter = WPExporter(
                    site,
                    site_host=self.tree.args['--site-host'],
                    site_path=self.full_name(),
                    output_dir=self.tree.args['--output-dir'],
                    wp_cli=self.container_name
                )
                wp_exporter.import_all_data_to_wordpress()
            except Exception as err:
                logging.error("%s - generate - Could not run site: %s", self.name, err)
        else:
            logging.error("%s - generate - Could not start Apache in %s", self.name, MAX_WORDPRESS_STARTING_TIME)


    def run_list_boxes(self, outfile_name):
        # built up Wordpress URL and composition_path
        #wp_url = "%s/%s" % (WP_HOST, self.full_name())
        #   composition_path = os.path.join(self.get_composition_dir(self.tree.args), self.container_name)

        outfile = open(outfile_name, 'a')

        ignored_boxes = ['text', 'faq']
        # FIXME : do not pass args in Objects
        self.tree.args['--site-path'] = self.full_name()
        self.tree.args['--wp-cli'] = self.container_name
        try:
            zip_file = SiteCrawler(self.name, self.tree.args).download_site()
            site_dir = unzip_one(self.tree.args['--output-dir'], self.name, zip_file)
            site = Site(site_dir, self.name)
            logging.info("Listing boxes for {}...".format(self.name))
            for page in site.pages_by_pid.values():

                #contents = {}
                #info_page = OrderedDict()

                for lang in page.contents.keys():
                    #contents[lang] = ""

                    # create the page content
                    for box in page.contents[lang].boxes:
                        #contents[lang] += box.content
                        if box.type not in ignored_boxes:
                            outfile.write("{}#!#{}#!#{}\n".format(box.type, box.content, page.url(lang)))
                        #print(box)

            shutil.rmtree(os.path.join(self.tree.args['--output-dir'], self.name))
            outfile.close()

        except Exception as err:
            logging.error("%s - generate - Could not run site: %s", self.name, err)



    def cleanup(self):
        # stop container
        composition_path = os.path.join(self.get_composition_dir(self.tree.args), self.container_name)
        UtilsGenerator.docker(composition_path, up=False)

        # remove Database
        if self.db_name is not None:
            cmd = r'docker exec wp-mariadb sh -c "mysql -u root' \
                r' --password=\"\$MYSQL_ROOT_PASSWORD\" --execute=\"DROP DATABASE %s;\""' % self.db_name
            logging.info(cmd)
            os.system(cmd)
