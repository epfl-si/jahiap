"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os
import timeit
import logging

import subprocess
from datetime import timedelta

from bs4 import BeautifulSoup
from wordpress_json import WordpressJsonWrapper, WordpressError

from exporter.utils import Utils
from settings import WP_USER, WP_PASSWORD, WP_PATH, CONFIGURED_LANGUAGES


class WPExporter:

    TRACER = "tracer_importing.csv"

    urls_mapping = []

    # Dictionary with the key 'wp_page_id' and the value 'wp_menu_id'
    menu_id_dict = {}

    @staticmethod
    def convert_bytes(num):
        """
        This function will convert bytes to MB.... GB... etc
        """
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def wp_cli(self, command):
        """
        Wrapper around the WP-CLI (wp-cli.org),
        official wordpress command line interface)
        available in the docker container wpcli
        """
        try:
            cmd = "docker exec %s wp --allow-root --path='%s' %s" \
                % (self.cli_container, self.path, command)
            logging.debug("exec '%s'", cmd)
            return subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError as err:
            logging.error("wp command failed : %s", cmd, stack_info=True)
            return None

    @classmethod
    def file_size(cls, file_path):
        """
        This function will return the file size
        """
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            return cls.convert_bytes(file_info.st_size)

    def __init__(self, site, cmd_args):
        """
        Site is the python object resulting from the parsing of Jahia XML
        Domain is the wordpress domain where to push the content
        """
        self.site = site
        self.host = cmd_args['--site-host']
        self.path = cmd_args['--site-path']
        self.elapsed = 0
        self.report = {
            'pages': 0,
            'files': 0,
            'menus': 0,
            'failed_files': 0,
            'failed_menus': 0,
            'failed_widgets': 0,
        }
        self.cli_container = cmd_args['--wp-cli'] or "wp-cli-%s" % self.site.name
        url = "http://%s/%s/?rest_route=/wp/v2" % (self.host, self.path)
        logging.info("setting up API on '%s', with %s:xxxxxx", url, WP_USER)
        self.wp = WordpressJsonWrapper(url, WP_USER, WP_PASSWORD)
        self.output_path = cmd_args['--output-dir']

    def import_all_data_to_wordpress(self):
        """
        Import all data to worpdress via REST API and wp-cli
        """
        try:
            start_time = timeit.default_timer()
            tracer_path = os.path.join(self.output_path, self.TRACER)

            self.align_languages()
            self.import_medias()
            self.import_pages()
            self.set_frontpage()
            self.populate_menu()
            self.import_sidebar()
            self.display_report()

            # log execution time
            elapsed = timedelta(seconds=timeit.default_timer() - start_time)
            logging.info("Data imported in %s", elapsed)

            with open(tracer_path, 'a', newline='\n') as tracer:
                tracer.write("%s, %s, %s, %s, %s\n" % (
                    self.site.name,
                    str(elapsed),
                    self.report['failed_files'],
                    self.report['failed_menus'],
                    self.report['failed_widgets'],
                ))
                tracer.flush()

        except WordpressError as err:
            logging.error("Exception while importing all data for %s: %s" % self.site, err, stack_info=True)
            with open(tracer_path, 'a', newline='\n') as tracer:
                tracer.write("%s, ERROR %s\n" % (self.site.name, str(err)))
                tracer.flush()

    def align_languages(self):
        if len(self.site.languages) == 1:
            for lang in (CONFIGURED_LANGUAGES - set(self.site.languages)):
                logging.info("Deleting language %s", lang)
                self.wp_cli('pll lang delete %s' % lang)

    def import_medias(self):
        """
        Import medias to Wordpress
        """
        logging.info("WP medias import start")
        for media in self.site.files:
            wp_media = self.import_media(media)
            if wp_media:
                self.replace_links(wp_media)
                self.report['files'] += 1

        logging.info("WP medias imported")

    def import_media(self, media):
        """
        Import a media to Wordpress
        """
        file_path = media.path + '/' + media.name
        file = open(file_path, 'rb')

        files = {
            'file': file
        }

        wp_media_info = {
            # date
            # date_gmt
            'slug': media.path,
            # status
            'title': media.name,
            # author
            # comment_status
            # ping_status
            # meta
            # template
            # alt_text
            # caption
            # description
            # post
        }
        files = files
        try:
            logging.debug("WP media information %s", wp_media_info)
            wp_media = self.wp.post_media(data=wp_media_info, files=files)
            return wp_media
        except Exception as e:
            logging.error("Import WP media failed: %s", e)
            self.report['failed_files'] += 1

    def replace_links(self, wp_media):
        """
        Replace links of the media 'wp_media' in all boxes
        """
        url = wp_media['source_url']

        for box in self.site.get_all_boxes():
            if "<img" in box.content:
                soup = BeautifulSoup(box.content, 'html.parser')
                img_tags = soup.find_all('img')
                for tag in img_tags:

                    extensions = ['.jpg', '.jpeg', '.png']
                    for extension in extensions:
                        elements = tag['src'].split(extension)[0].split('/')
                        index = len(elements) - 1
                        file_name = elements[index].replace(' ', '-') + extension

                        if file_name in url:
                            tag['src'] = url
                            box.content = str(soup)

    def update_parent_id(self):
        """
        Update all pages to define the pages hierarchy
        """
        for page in self.site.pages_by_pid.values():
            if page.parent:
                wp_page_info = {
                    'parent': page.parent.wp_id
                }
                if page.wp_id:
                    self.wp.post_pages(page_id=page.wp_id, data=wp_page_info)

    def import_pages(self):
        """
        Import all pages of jahia site to Wordpress
        """
        wp_pages = []
        for page in self.site.pages_by_pid.values():

            content = ""

            for lang in page.contents.keys():
                for box in page.contents[lang].boxes:
                    content += box.content

                wp_page_info = {
                    # date: auto => date/heure du jour
                    # date_gmt: auto => date/heure du jour GMT
                    'slug': page.contents[lang].path,
                    'status': 'publish',
                    # password
                    'title': page.contents[lang].title,
                    'content': content,
                    # author
                    # excerpt
                    # featured_media
                    # comment_status: 'closed'
                    # ping_status: 'closed'
                    # format
                    # meta
                    # sticky
                    # template
                    # categories
                    # tags
                }

                wp_page = self.wp.post_pages(data=wp_page_info)
                wp_pages.append(wp_page)

                mapping = {
                    'jahia_url': page.contents[lang].path,
                    'wp_url': wp_page['link']
                }

                self.urls_mapping.append(mapping)
                logging.info("WP page '%s' created", wp_page['link'])

                # keep wordpress ID for further usages
                page.wp_id = wp_page['id']
                self.report['pages'] += 1

                # Set page language
                result = self.wp_cli('polylang set post %s %s' % (page.wp_id, lang))
                if not result is None:
                    logging.debug("page.%s lang set to '%s'", page.wp_id, lang)

        self.update_parent_id()

    def import_sidebar(self):
        """
        import sidebar via vpcli
        """
        try:
            for lang in self.site.homepage.contents.keys():
                for box in self.site.homepage.contents[lang].sidebar.boxes:
                    content = Utils.escape_quotes(box.content)
                    cmd = 'widget add black-studio-tinymce page-widgets ' \
                        '--title="%s" --text="%s"' % (box.title, content)
                    self.wp_cli(cmd)
            logging.info("WP all sidebar imported")

        except WordpressError as e:
            self.report['failed_widgets'] += 1

    def create_submenu(self, page):
        """
        Create recursively submenus.
        """
        if page.wp_id and page not in self.site.homepage.children and page.parent.wp_id in self.menu_id_dict:

            parent_menu_id = self.menu_id_dict[page.parent.wp_id]

            command = 'menu item add-post Main %s --parent-id=%s --porcelain' % (page.wp_id, parent_menu_id)
            menu_id = self.wp_cli(command)
            self.menu_id_dict[page.wp_id] = Utils.get_menu_id(menu_id)
            self.report['menus'] += 1

        if page.has_children():
            for child in page.children:
                self.create_submenu(child)

    def populate_menu(self):
        """
        Add pages into the menu in wordpress.
        This menu needs to be created before hand.
        """
        try:
            # Create homepage menu
            page = self.site.homepage
            menu_id = self.wp_cli('menu item add-post Main %s --classes=link-home --porcelain' % page.wp_id)
            self.menu_id_dict[page.wp_id] = Utils.get_menu_id(menu_id)
            self.report['menus'] += 1

            # Create children of homepage menu
            for homepage_children in self.site.homepage.children:
                if homepage_children.wp_id:
                    menu_id = self.wp_cli('menu item add-post Main %s --porcelain' % homepage_children.wp_id)
                    self.menu_id_dict[homepage_children.wp_id] = Utils.get_menu_id(menu_id)
                    self.report['menus'] += 1

                # create recursively submenus
                self.create_submenu(homepage_children)

            logging.info("WP menus populated")

        except WordpressError as e:
            self.report['failed_menus'] += 1

    def set_frontpage(self):
        """
        Use wp-cli to set the two worpress options needed fotr the job
        """
        # sanity check on homepage
        if not self.site.homepage:
            raise Exception("No homepage defined for site")

        # make sure that we have a worpress id
        if not getattr(self.site.homepage, 'wp_id'):
            raise Exception("Run 'import_pages' before 'set_frontpage'")

        # call wp-cli
        frontpage_id = self.site.homepage.wp_id
        self.wp_cli('option update show_on_front page')

        result = self.wp_cli('option update page_on_front %s' % frontpage_id)
        if not result is None:
            logging.info("WP frontpage setted")

    def delete_all_content(self):
        """
        Delete all content WordPress
        """
        self.delete_medias()
        self.delete_pages()
        self.delete_widgets()

    def delete_medias(self):
        """
        Delete medias in WordPress via WP REST API
        HTTP delete  http://.../wp-json/wp/v2/media/1761?force=true
        """
        logging.info("Deleting medias...")
        medias = self.wp.get_media(params={'per_page': '100'})
        while len(medias) != 0:
            for media in medias:
                self.wp.delete_media(media_id=media['id'], params={'force': 'true'})
            medias = self.wp.get_media(params={'per_page': '100'})
        logging.info("All medias deleted")

    def delete_pages(self):
        """
        Delete all pages in Wordpress via WP REST API
        HTTP delete /wp-json/wp/v2/pages/61?force=true
        """
        pages = self.wp.get_pages(params={'per_page': '100'})
        while len(pages) != 0:
            for page in pages:
                self.wp.delete_pages(page_id=page['id'], params={'force': 'true'})
            pages = self.wp.get_pages(params={'per_page': '100'})
        logging.info("All pages and menus deleted")

    def delete_widgets(self):
        """
        Delete all widgets
        """
        cmd = "widget list page-widgets --fields=id --format=csv"
        widgets_id_list = self.wp_cli(cmd).decode("UTF-8").split("\n")[1:-1]
        for widget_id in widgets_id_list:
            cmd = "widget delete " + widget_id
            self.wp_cli(cmd)
        logging.info("All widgets deleted")

    def display_report(self):
        """
        Display report
        """

        result = """
Imported in WordPress :

  - %s files

  - %s pages

  - %s menus

Errors :

  - %s files

""" % (self.report['files'], self.report['pages'], self.report['menus'], self.report['failed_files'])

        print(result)

    def generate_nginx_conf_file(self):
        """
        Generates a nginx configuration file containing
        the rewrites of the pages jahia in WordPress page.
        """

        first_part = """
server {
    server_name %(site_name)s.epfl.ch ;
    return 301 $scheme://test-web-static.epfl.ch/%(WP_PATH)s/%(site_name)s$request_uri;
}

server {
    listen       80;
    listen       [::]:80;

""" % {'site_name': self.site.name, "WP_PATH": WP_PATH}

        last_part = """
    location / {
        proxy_pass   http://traefik/;
    }
}
"""
        # Add the first part of the content file
        content = first_part

        # Add all rewrite jahia URI to WordPress URI
        for element in self.urls_mapping:

            line = """    rewrite ^/%(WP_PATH)s/%(site_name)s/%(jahia_url)s$ /%(WP_PATH)s/%(site_name)s/%(wp_url)s permanent;
""" % {
                'site_name': self.site.name,
                'jahia_url': element['jahia_url'][1:],
                'wp_url': element['wp_url'].split("/")[3],
                "WP_PATH": WP_PATH,
            }
            content += line

        # Add the last part of the content file
        content += last_part

        # Set the file name
        file_name = os.path.join(self.output_path, 'jahia-%s.conf' % self.site.name)

        # Open the file in write mode
        with open(file_name, 'a') as f:
            f.write(content)
