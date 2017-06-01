"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
import os

from bs4 import BeautifulSoup
from wordpress_json import WordpressJsonWrapper

from settings import DOMAIN, WP_USER, WP_PASSWORD


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
    def file_size(cls, file_path):
        """
        this function will return the file size
        """
        if os.path.isfile(file_path):
            file_info = os.stat(file_path)
            return cls.convert_bytes(file_info.st_size)

    def __init__(self, site):
        self.site = site
        url = DOMAIN + "/index.php/wp-json/wp/v2"
        self.wp = WordpressJsonWrapper(url, WP_USER, WP_PASSWORD)

    def import_all_data_in_wordpress(self):
        self.import_medias()
        self.import_pages()
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

            page = self.wp.post_pages(data=wp_page_info)
            self.report['pages'] += 1

            # Add menu element
            os.system('docker exec wpcli wp menu item add-post Main %s' % page['id'])
            self.report['menus'] += 1

    def display_report(self):

        result = """
Found in wordpress :

  - %s files

  - %s pages

  - %s menus

""" % (self.report['files'], self.report['pages'], self.report['menus'])

        print(result)
