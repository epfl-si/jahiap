"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017

    Testing the generator script
"""
import os
import shutil
import pytest
import logging
import time
import requests
from datetime import datetime

from generator.tree import Tree
from generator.utils import Utils as GeneratorUtils
from utils import Utils
from settings import DATA_PATH, WP_HOST


@pytest.fixture(scope='module')
def generated_tree(request):
    """ Using following tree structure:
        root
        ├── administratif (list)
        │      ├── building2050 (site)
        │      └── apc (site)
        ├── ahead (site)
        │      └── bioinspired (site)
        └── labs (list)
                  └── apml (site)
    """
    output_path = TestGenerator.ARGS['--output-dir']
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    sites = GeneratorUtils.csv_to_dict(file_path=TestGenerator.DATA_FILE)
    tree = Tree(TestGenerator.ARGS, sites=sites)
    tree.prepare_run()
    return tree


class TestTreeStructure(object):

    def test_children(self, generated_tree):
        assert len(generated_tree.root.children) == 3
        assert len(generated_tree.nodes['administratif'].children) == 2
        assert len(generated_tree.nodes['ahead'].children) == 1
        assert len(generated_tree.nodes['bioinspired'].children) == 0
        assert len(generated_tree.nodes['labs'].children) == 1
        assert len(generated_tree.nodes['apml'].children) == 0

    def test_parents(self, generated_tree):
        assert generated_tree.root.parent is None
        assert generated_tree.nodes['administratif'].parent == generated_tree.root
        assert generated_tree.nodes['ahead'].parent == generated_tree.root
        assert generated_tree.nodes['bioinspired'].parent == generated_tree.nodes['ahead']
        assert generated_tree.nodes['labs'].parent == generated_tree.root
        assert generated_tree.nodes['apml'].parent == generated_tree.nodes['labs']

    def test_full_name(self, generated_tree):
        assert generated_tree.root.full_name() == ""
        assert generated_tree.nodes['administratif'].full_name() == "administratif"
        assert generated_tree.nodes['ahead'].full_name() == "ahead"
        assert generated_tree.nodes['bioinspired'].full_name() == "ahead/bioinspired"
        assert generated_tree.nodes['labs'].full_name() == "labs"
        assert generated_tree.nodes['apml'].full_name() == "labs/apml"


class TestGenerator(object):

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
        # skip the test if traefik not running
        if not Utils.is_traefik_running():
            pytest.skip("not testing docker... needs traefik running from helpers module")

        # run docker for the root node
        logging.info("Running docker for %s", generated_tree.root.name)
        generated_tree.root.run()

        # allow nginx to start up
        time.sleep(0.3)

        # test root URL
        root_url = "http://"+WP_HOST
        req = requests.get(root_url)
        assert req.status_code == 200
        assert b"<title>EPFL</title>" in req.content

        # clean up a bit
        os.system("docker rm -f generated-%s" % generated_tree.root.name)
