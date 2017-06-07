#!/usr/local/bin/python
"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

from jinja2 import Environment, PackageLoader, select_autoescape

import os


class Exporter:

    env = Environment(
        loader=PackageLoader('exporter', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    def __init__(self, site, out_path):

        self.site = site
        self.out_path = out_path
        self.sitemap_content = ""
        self.navigation = "<!-- START NAVIGATION -->\n"

        # create the output path if necessary
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        self.generate_pages()

        self.extract_files()

    def generate_pages(self):
        """Generate the pages & the sitemap"""

        # update the boxes data
        self.update_boxes_data()

        # navigation
        self.generate_navigation(self.site.homepage)

        # regular pages
        template = self.env.get_template('epfl-sidebar-en.html')

        for page in self.site.pages:
            content = template.render(page=page, site=self.site, exporter=self)

            self.generate_page(page.name, content)

        # sitemap
        template = self.env.get_template('epfl-sitemap-en.html')

        self.generate_sitemap_content(self.site.homepage)

        content = template.render(page=None, site=self.site, exporter=self)

        self.generate_page("sitemap.html", content)

    def update_boxes_data(self):
        """Update the boxes data"""
        for page in self.site.pages:
            for box in page.boxes:
                # toggle box : add EPFL bootstrap specific code
                if box.type == "toggle":
                    # toggle title
                    content = "<h3 data-widget='collapse'>%s</h3>" % box.title
                    # toggle content
                    content += "<div>%s</div>" % box.content

                    box.content = content

                    # we don't want to show the box title
                    box.title = None

                # all other box types, we just enclose them in a div
                else:
                    box.content = "<div>" + box.content + "</div>"

    def generate_page(self, name, content):
        """Generate a page"""
        path = "%s/%s" % (self.out_path, name)

        file = open(path, "w")

        file.write(content)

        file.close()

    def generate_navigation(self, page):
        """
        Generate the navigation content. This is a recursive method
        """
        if not page.is_homepage():
            # current page
            self.navigation_spacer(page)
            self.navigation += "<li class='nav-item'><a class='nav-link' href='/%s'>%s</a>" % (page.name, page.title)

        if page.has_children():
            if not page.is_homepage():
                self.navigation += "\n"
                self.navigation_spacer(page)
                self.navigation += "<ul class='nav-list nav-vertical' data-widget='menu'>\n"

            for child in page.children:
                # recursive call
                self.generate_navigation(child)

            if not page.is_homepage():
                self.navigation_spacer(page)
                self.navigation += "</ul>\n</li>\n"
        else:
            if not page.is_homepage():
                self.navigation += "</li>\n"

    def navigation_spacer(self, page):
        """Add spaces according to the page level"""
        for i in range(page.level - 1):
            self.navigation += "  "

    def generate_sitemap_content(self, page):
        """
        Generate the sitemap content. This is a recursive method
        """
        # top <ul> for the homepage
        if page.is_homepage():
            self.sitemap_content += "<ul>"

        # current page
        self.sitemap_content += "<li><a href='/%s'>%s</a>" % (page.name, page.title)

        if page.has_children():
            self.sitemap_content += "<ul>"

            for child in page.children:
                # recursive call
                self.generate_sitemap_content(child)

            self.sitemap_content += "</ul></li>"
        else:
            self.sitemap_content += "</li>"

        # top <ul> for the homepage
        if page.is_homepage():
            self.sitemap_content += "</ul>"

    def extract_files(self):
        """Extract the files"""

        start = "%s/content/sites/%s/files" % (self.site.base_path, self.site.name)

        for (path, dirs, files) in os.walk(start):
            for file in files:
                # we exclude the thumbnails
                if "thumbnail" == file or "thumbnail2" == file:
                    continue

                src = "%s/%s" % (path, file)

                dst = self.out_path + src[src.index("files/") - 1:]

                dst = dst[:dst.rindex("/")]

                parent = dst[:dst.rindex("/")]

                # create the parent directory if necessary
                if not os.path.exists(parent):
                    cmd = "mkdir -p '%s'" % parent
                    os.system(cmd)

                # now copy the file
                cmd = "cp '%s' '%s'" % (src, dst)
                os.system(cmd)
