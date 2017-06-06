"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

from bs4 import BeautifulSoup
from wordpress_json import WordpressJsonWrapper

from settings import WP_USER, WP_PASSWORD


class WP_Exporter:

    report = {
        'pages': 0,
        'files': 0,
        'menus': 0,
    }

    @staticmethod
    def convert_bytes(num):
        """
        this function will convert bytes to MB.... GB... etc
        """
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    @classmethod
    def wp_cli(cls, command):
        """
            Wrapper around the WP-CLI (wp-cli.org),
            official wordpress command line interface)
            available in the docker container wpcli
        """
        os.system('docker exec wpcli %s' % command)

    @classmethod
    def file_size(cls, file_path):
        """
        this function will return the file size
        """
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            return cls.convert_bytes(file_info.st_size)

    def __init__(self, site, domain):
        """
            site is the python object resulting from the parsing of Jahia XML
            domain is the wordpress domain where to push the content
        """
        self.site = site
        url = "http://%s/index.php/wp-json/wp/v2" % domain
        self.wp = WordpressJsonWrapper(url, WP_USER, WP_PASSWORD)

    def import_all_data_in_wordpress(self):
        self.import_medias()
        self.import_pages()
        self.set_frontpage()
        self.populate_menu('Main')
        self.display_report()

    def import_media(self, media):

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
        return self.wp.post_media(data=wp_media_info, files=files)

    def replace_links(self, wp_media):

        url = wp_media['source_url']

        for page in self.site.pages:
            for box in page.boxes:
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

    def import_medias(self):

        for media in self.site.files:
            wp_media = self.import_media(media)
            self.replace_links(wp_media)
            self.report['files'] += 1

    def import_pages(self):

        for page in self.site.pages:

            content = ""
            for box in page.boxes:
                content += box.content

            wp_page_info = {
                # date: auto => date/heure du jour
                # date_gmt: auto => date/heure du jour GMT
                'slug': page.name,
                'status': 'publish',
                # password
                'title': page.title,
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

            # keep wordpress ID for further usages
            page.wp_id = wp_page['id']
            self.report['pages'] += 1

    def populate_menu(self, menu_name):
        """
            Add pages into the menu in wordpress with given menu_name.
            This menu needs to be created before hand
        """
        for page in self.site.pages:
            # add page to menu
            self.wp_cli('wp menu item add-post %s %s' % (menu_name, page.wp_id))
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

    def display_report(self):

        result = """
Found in wordpress :

  - %s files

  - %s pages

  - %s menus

""" % (self.report['files'], self.report['pages'], self.report['menus'])

        print(result)
