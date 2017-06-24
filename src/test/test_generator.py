# -*- coding: utf-8 -*-
"""
    Testing the crawl.py script
"""
import os
import shutil
import pytest
import logging
import requests
from datetime import datetime

from settings import DATA_PATH, WP_HOST
from generator.node import Tree, RootNode, ListNode, SiteNode


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


@pytest.fixture(scope='module')
def generated_tree(request):
        output_path = TestGenerator.ARGS['--output-dir']
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        tree = Tree(TestGenerator.ARGS, filename=TestGenerator.DATA_FILE)
        tree.create_html()
        return tree


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

    WORKING_PATH = os.path.join(DATA_PATH, "full-tree")
    DATA_FILE = os.path.join(WORKING_PATH, "sites.csv")
    OUTPUT_DIR = os.path.join(WORKING_PATH, "output-by-test")
    OUTPUT_PATH = os.path.join(OUTPUT_DIR, "generator")

    ARGS = {
        '--output-dir': OUTPUT_DIR,
        '--export-path': WORKING_PATH,
        '--date': datetime.today().strftime("%Y-%m-%d-%H-%M"),
        '--force': False,
    }

    def test_output_path(self, generated_tree):
        assert os.path.exists(TestGenerator.OUTPUT_PATH)

    def test_root_path(self, generated_tree):
        root_path = os.path.join(TestGenerator.OUTPUT_PATH, "index.html")
        assert os.path.isfile(root_path)

    def test_list_paths(self, generated_tree):
        administratif_path = os.path.join(TestGenerator.OUTPUT_PATH, "administratif")
        labs_path = os.path.join(TestGenerator.OUTPUT_PATH, "labs")
        assert os.path.isdir(administratif_path)
        assert os.path.isfile(os.path.join(administratif_path, "index.html"))
        assert os.path.isdir(labs_path)
        assert os.path.isfile(os.path.join(labs_path, "index.html"))

    def test_apc_site_path(self, generated_tree):
        apc_path = os.path.join(TestGenerator.OUTPUT_PATH, "apc")
        assert os.path.isdir(apc_path)
        assert os.path.isfile(os.path.join(apc_path, "administratif/apc/index-fr.html"))

    def test_ahead_site_path(self, generated_tree):
        ahead_path = os.path.join(TestGenerator.OUTPUT_PATH, "ahead")
        assert os.path.isdir(ahead_path)
        assert os.path.isfile(os.path.join(ahead_path, "ahead/index.html"))

    def test_bioinspired_site_path(self, generated_tree):
        bioinspired_path = os.path.join(TestGenerator.OUTPUT_PATH, "bioinspired")
        assert os.path.isdir(bioinspired_path)
        assert os.path.isfile(os.path.join(bioinspired_path, "ahead/bioinspired/index.html"))


class TestDockerCreation(object):

    def test_root_url(self, generated_tree):
        # run docker for the root node
        logging.info("Running docker for %s", generated_tree.root.name)
        generated_tree.root.run()

        # test root URL
        root_url = "http://"+WP_HOST
        req = requests.get(root_url)
        assert req.status_code == 200
        assert b"<title>EPFL</title>" in req.content

        # clean up a bit
        os.system("docker rm -f generated-%s" % generated_tree.root.name)
