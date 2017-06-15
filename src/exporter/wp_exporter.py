"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

from bs4 import BeautifulSoup
from wordpress_json import WordpressJsonWrapper, WordpressError

from settings import WP_USER, WP_PASSWORD
from utils import Utils


class WPExporter:

    report = {
        'pages': 0,
        'files': 0,
        'menus': 0,
        'failed_files': 0,
    }

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
        os.system('docker exec wp-cli-%s %s' % (self.site, command))

    @classmethod
    def file_size(cls, file_path):
        """
        This function will return the file size
        """
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            return cls.convert_bytes(file_info.st_size)

    def __init__(self, site, domain):
        """
        Site is the python object resulting from the parsing of Jahia XML
        Domain is the wordpress domain where to push the content
        """
        self.site = site
        url = "http://%s/?rest_route=/wp/v2" % domain
        self.wp = WordpressJsonWrapper(url, WP_USER, WP_PASSWORD)

    def import_all_data_to_wordpress(self):
        """
        Import all data to worpdress via REST API and wp-cli
        """
        self.import_medias()
        self.import_pages()
        self.set_frontpage()
        self.populate_menu(menu_name='Main')
        self.import_sidebar()
        self.display_report()

    def import_medias(self):
        """
        Import medias to Wordpress
        """
        for media in self.site.files:
            wp_media = self.import_media(media)
            if wp_media:
                self.replace_links(wp_media)
                self.report['files'] += 1

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
            wp_media = self.wp.post_media(data=wp_media_info, files=files)
            return wp_media
        except WordpressError as e:
            self.report['failed_files'] += 1
            # print(file.name)

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
                self.wp.post_pages(page_id=page.wp_id, data=wp_page_info)

    def import_pages(self):
        """
        Import all pages of jahia site to Wordpress
        """
        wp_pages = []
        for page in self.site.pages_by_pid.values():

            content = ""
            if 'en' in page.contents:
                for box in page.contents['en'].boxes:
                    content += box.content

                wp_page_info = {
                    # date: auto => date/heure du jour
                    # date_gmt: auto => date/heure du jour GMT
                    'slug': page.contents['en'].path,
                    'status': 'publish',
                    # password
                    'title': page.contents['en'].title,
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

                # keep wordpress ID for further usages
                page.wp_id = wp_page['id']
                self.report['pages'] += 1

        self.update_parent_id()

    def import_sidebar(self):
        """
        import sidebar via vpcli
        """
        for box in self.site.homepage.contents["en"].sidebar.boxes:
            content = Utils.escape_quotes(box.content)
            cmd = 'wp widget add black-studio-tinymce page-widgets ' \
                  '--title="%s" --text="%s"' % (box.title, content)
            self.wp_cli(cmd)

    def populate_menu(self, menu_name):
        """
        Add pages into the menu in wordpress with given menu_name.
        This menu needs to be created before hand
        """

        # Create homepage menu
        page = self.site.homepage
        self.wp_cli('wp menu item add-post %s %s' % (menu_name, page.wp_id))
        self.report['menus'] += 1

        # Create children homepage menu
        for children in self.site.homepage.children:
            self.wp_cli('wp menu item add-post %s %s' % (menu_name, children.wp_id))
            self.report['menus'] += 1

        # Create others menus
        for page in self.site.pages_by_pid.values():
            if page.parent and not page.parent.is_homepage():
                self.wp_cli('wp menu item add-post %s %s --parent-id=%s' % (menu_name, page.wp_id, page.parent.wp_id))
            self.report['menus'] += 1

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
        self.wp_cli('wp option update show_on_front page')
        self.wp_cli('wp option update page_on_front %s' % frontpage_id)

    def delete_all_content(self):
        """
        Delete all content Worpress
        """
        self.delete_medias()
        self.delete_pages()

    def delete_medias(self):
        """
        Delete medias in Wordpress via WP REST API
        HTTP delete  http://.../wp-json/wp/v2/media/1761?force=true
        """
        medias = self.wp.get_media(params={'per_page': '100'})
        while len(medias) != 0:
            for media in medias:
                self.wp.delete_media(media_id=media['id'], params={'force': 'true'})
            medias = self.wp.get_media(params={'per_page': '100'})

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

    def delete_widgets(self):
        """
        Delete all widgets
        """
        cmd = "wp widget list page-widgets --fields=id"
        widgets_id_list = self.wp_cli(cmd)
        for widget_id in widgets_id_list:
            cmd = "wp widget delete " + widget_id
            self.wp_cli(cmd)

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
