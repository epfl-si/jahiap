import os
import pytest

from settings import DATA_PATH
from test import Data


def get_sites():
    """
    Return the list of jahia sites
    """
    for top, dirs, files in os.walk(DATA_PATH):
        return dirs


@pytest.fixture(scope='module', params=get_sites())
def site(request):
    """
    Load site only once
    """
    from jahiap import Site
    site_name = request.param
    site_data_path = DATA_PATH + request.param
    return Site(site_data_path, site_name)


@pytest.fixture()
def data(site):
    """
    return the data of one jahia site
    """
    dictionary_name = site.name + "_data"
    return Data.__getattribute__(Data, dictionary_name)


class TestSiteProperties:
    """
      Check main properties of 'site' website
    """

    def test_name(self, site, data):
        assert site.name == data['properties']['name']

    def test_title(self, site, data):
        assert site.title == data['properties']['title']

    def test_acronym(self, site, data):
        assert site.acronym == data['properties']['acronym']

    def test_theme(self, site, data):
        assert site.theme == data['properties']['theme']

    def test_breadcrumb_title(self, site, data):
        assert site.breadcrumb_title == data['properties']['breadcrumb_title']

    def test_breadcrumb_url(self, site, data):
        assert site.breadcrumb_url == data['properties']['breadcrumb_url']

    def test_css_url(self, site, data):
        assert site.css_url == data['properties']['css_url']


class TestSiteStructure:
    """
      Check main elements of 'site' website
    """

    def test_nb_pages(self, site, data):
        assert len(site.pages) == len(data['pages'])

    def test_page_ids(self, site, data):
        expected_pids = set([page['pid'] for page in data['pages']])
        pids = set([p.pid for p in site.pages])
        assert expected_pids == pids

    def test_nb_boxes(self, site, data):
        expected_boxes = sum([page['nb_boxes'] for page in data['pages']])
        boxes = sum([len(p.boxes) for p in site.pages])
        assert expected_boxes == boxes

    def test_nb_files(self, site, data):
        assert len(site.files) == data['files']


class TestSidebar:
    """
      Check content of sidebar
    """
    def test_box(self, site, data):

        for data_page in data['pages']:
            for page in site.pages:
                if page.pid == data_page['pid']:

                    # Nb boxes
                    assert len(data_page['sidebar']) == len(page.sidebar.boxes)

                    # Box title
                    titles = [box.title for box in page.sidebar.boxes]
                    expected_titles = [data_box['title'] for data_box in data_page['sidebar']]
                    assert titles == expected_titles

                    # Box content
                    contents = [box.content for box in page.sidebar.boxes]
                    expected_contents = [data_box['content'] for data_box in data_page['sidebar']]
                    assert contents == expected_contents

                    # Box type
                    expected_type = [box.type for box in page.sidebar.boxes]
                    type = [data_box['type'] for data_box in data_page['sidebar']]
                    assert expected_type == type


# class TestHomepage:
#   """
#     Check main properties & some content of DCSL's frontpage
#   """
#
#   def test_pid(self, site):
#     assert site.homepage.pid == "115349"
#
#   def test_uuid(self, site):
#     assert site.homepage.uuid == "51cc1e42-e0d6-4103-8688-2c3f5a31645a"
#
#   def test_original_uuid(self, site):
#     assert site.homepage.original_uuid == "99b07ab2-69d7-493d-adb7-bf1c0f4bbb3c"
#
#   def test_url_mapping(self, site):
#     assert site.homepage.vanity_url == "dcsl"
#
#   def test_template(self, site):
#     assert site.homepage.template == "home"
#
#   def test_primary_type(self, site):
#     assert site.homepage.primary_type == "epfl:home"
#
#   def test_title(self, site):
#     assert site.homepage.title == "DCSL"
#
#   def test_acl(self, site):
#     assert site.homepage.acl == "u:223767:rwa|u:229105:rwa|u:196571:rwa|u:190526:rwa|g:DCSL-unit:rwa|g:guest:r--|g:jahia-admins:rwa|none" # noqa
#
#   def test_content(self, site):
#     contents = [box.content for box in site.homepage.boxes]
#     assert len(contents) == 3
#     expected_contents = [
#       "files/Servers lab pic.jpg",
#       "IX -- a specialized operating system",
#       "We would like to thank our sponsors"
#     ]
#     for content, expected_content in zip(contents, expected_contents):
#       assert expected_content in content
