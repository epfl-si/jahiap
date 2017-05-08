#!/usr/local/bin/python

from jinja2 import Environment, PackageLoader, select_autoescape

import os

class Exporter:

    def __init__(self, site, out_path):

        self.site = site
        self.out_path = out_path

        # create the output path
        cmd = "mkdir %s" % self.out_path
        os.system(cmd)

        env = Environment(
            loader=PackageLoader('exporter', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

        template = env.get_template('epfl-en.html')

        for page in self.site.pages.values():

            path = "%s/%s" % (self.out_path, page.name)

            content = template.render(page=page)

            html_file = open(path, "w")

            html_file.write(content)

            html_file.close()
