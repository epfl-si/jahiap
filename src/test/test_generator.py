# -*- coding: utf-8 -*-
"""
    Testing the crawl.py script
"""
import os
import shutil
import pytest
import requests
from datetime import datetime

from settings import DATA_PATH, WP_HOST
from generator.node import Generator, RootNode, ListNode, SiteNode


@pytest.fixture(scope='module')
def basic_tree(request):
    """
    Prepare a basic tree structure for the tests:
        root/
        ├── IC
        │      └── blabla
        ├── SI
        │      └── VPSI
        └── labs
                  ├── DCSL
                  └── master
    """
    root = RootNode("")

    ic_node = SiteNode("IC")
    blabla_node = SiteNode("blabla")

    # creating instances with explicit parents
    si_node = ListNode("SI")
    vpsi_node = SiteNode("VPSI")

    labs_node = ListNode("labs")
    dcsl_node = SiteNode("DCSL")
    master_node = SiteNode("master")

    # setting all parents
    ic_node.parent = root
    si_node.parent = root
    labs_node.parent = root
    blabla_node.parent = ic_node
    vpsi_node.parent = si_node
    dcsl_node.parent = labs_node
    master_node.parent = labs_node

    # setting all children
    root.children = [si_node, ic_node, labs_node]
    si_node.children = [vpsi_node]
    ic_node.children = [blabla_node]
    labs_node.children = [dcsl_node, master_node]

    return root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node

@pytest.fixture(scope='module')
def generated_tree(request):
        output_path = TestGenerator.ARGS['--output-dir']
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        return Generator(TestGenerator.ARGS).run(TestGenerator.DATA_FILE)

class TestTreeStructure(object):

    def test_children(self, basic_tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = basic_tree
        assert len(root.children) == 3
        assert len(ic_node.children) == 1
        assert len(blabla_node.children) == 0
        assert len(labs_node.children) == 2
        assert len(vpsi_node.children) == 0
        assert len(dcsl_node.children) == 0

    def test_full_name(self, basic_tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = basic_tree
        assert root.full_name() == "/"
        assert ic_node.full_name() == "/IC"
        assert blabla_node.full_name() == "/IC/blabla"
        assert labs_node.full_name() == "/labs"
        assert vpsi_node.full_name() == "/SI/VPSI"
        assert dcsl_node.full_name() == "/labs/DCSL"

class TestGenerator(object):
    """
    Using following tree structure:
        root
        ├── administratif (list)
        │      ├── building2050
        │      └── apc
        ├── ahead (site)
        │      └── bioinspired
        └── labs (list)
                  └── apml
    """

    WORKING_PATH = os.path.join(DATA_PATH, "generator")
    DATA_FILE = os.path.join(WORKING_PATH, "sites.csv")

    ARGS = {
        '--output-dir': os.path.join(WORKING_PATH, "tmp"),
        '--date': datetime.today().strftime("%Y-%m-%d-%H-%M"),
        '--force': False,
    }

    def test_output_path(self, generated_tree):
        assert os.path.exists(TestGenerator.WORKING_PATH)

    def test_root_path(self, generated_tree):
        root_path = os.path.join(TestGenerator.WORKING_PATH, "index.html")
        assert os.path.isfile(root_path)

    def test_list_paths(self, generated_tree):
        administratif_path = os.path.join(TestGenerator.WORKING_PATH, "administratif")
        labs_path = os.path.join(TestGenerator.WORKING_PATH, "labs")
        assert os.path.isdir(administratif_path)
        assert os.path.isfile(os.path.join(administratif_path, "index.html"))
        assert os.path.isdir(labs_path)
        assert os.path.isfile(os.path.join(labs_path, "index.html"))

    def test_apc_site_path(self, generated_tree):
        apc_path = os.path.join(TestGenerator.WORKING_PATH, "apc")
        assert os.path.isdir(os.path.join(apc_path, "apc"))
        assert os.path.isfile(os.path.join(apc_path, "admnistratif/apc/index.html"))

    def test_ahead_site_path(self, generated_tree):
        ahead_path = os.path.join(TestGenerator.WORKING_PATH, "ahead")
        assert os.path.isdir(os.path.join(ahead_path, "ahead"))
        assert os.path.isfile(os.path.join(ahead_path, "ahead/index.html"))

    def test_bioinspired_site_path(self, generated_tree):
        bioinspired_path = os.path.join(TestGenerator.WORKING_PATH, "bioinspired")
        assert os.path.isdir(os.path.join(bioinspired_path, "bioinspired"))
        assert os.path.isfile(os.path.join(bioinspired_path, "ahead/bioinspired/index.html"))

    def test_root_url(self, generated_tree):
        root_url = "http://"+WP_HOST
        req = requests.get(root_url)
        assert req.status_code == 200
        assert "<title>EPFL</title>" in req.content

    def test_list_urls(self, generated_tree):
        administratif_url = "http://"+WP_HOST+"/administratif"
        administratif_req = requests.get(administratif_url)
        assert administratif_req.status_code == 200
        assert "<title>administratif</title>" in administratif_req.content
        # labs
        labs_url = "http://"+WP_HOST+"/administratif"
        labs_req = requests.get(labs_url)
        assert labs_req.status_code == 200
        assert "<title>administratif</title>" in labs_req.content