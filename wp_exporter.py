"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

from wordpress_json import WordpressJsonWrapper


class WP_Exporter:

    def __init__(self, site):

        self.site = site
        self.wp = WordpressJsonWrapper('http://localhost/monsiteweb/index.php/wp-json/wp/v2', 'admin', 'admin')

    def generate_pages(self):

        for page in self.site.pages.values():

            wp_page_info = {}
            wp_page_info['title'] = page.title

            wp_page = self.wp.post_pages(data=wp_page_info)
