# -*- coding: utf-8 -*-
"""
    Testing the crawl.py script
"""
import pytest

from generator.node import RootNode, ListNode, SiteNode


@pytest.fixture(scope='module')
def tree(request):
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

    def test_simplest_init(self, tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = tree
        assert root.name == ""

    def test_children(self, tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = tree
        assert len(root.children) == 3
        assert len(ic_node.children) == 1
        assert len(blabla_node.children) == 0
        assert len(labs_node.children) == 2
        assert len(vpsi_node.children) == 0
        assert len(dcsl_node.children) == 0


class TestBasicFunctions(object):

    def test_full_name(self, tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = tree
        assert root.full_name() == "/"
        assert ic_node.full_name() == "/IC"
        assert blabla_node.full_name() == "/IC/blabla"
        assert labs_node.full_name() == "/labs"
        assert vpsi_node.full_name() == "/SI/VPSI"
        assert dcsl_node.full_name() == "/labs/DCSL"
