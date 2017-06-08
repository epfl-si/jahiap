"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""


class DictExporter:

    @staticmethod
    def generate_data(site):
        """Generate data for tests"""
        data = {}

        # properties
        data['properties'] = {
            'name': site.name,
            'title': site.title,
            'acronym': site.acronym,
            'theme': site.theme,
            'breadcrumb_title': site.breadcrumb_title,
            'breadcrumb_url': site.breadcrumb_url,
            'css_url': site.css_url
        }

        # pages
        #
        data['pages'] = []
        for page in site.pages:

            box_list = []
            for box in page.sidebar.boxes:
                box_dict = {
                    'title': box.title,
                    'content': box.content,
                    'type': box.type
                }
                box_list.append(box_dict)

            page_dict = {
                'pid': page.pid,
                'title': page.title,
                'nb_boxes': len(page.boxes),
                'sidebar': box_list
            }
            data['pages'].append(page_dict)

        # files
        data['files'] = len(site.files)

        print(data)
