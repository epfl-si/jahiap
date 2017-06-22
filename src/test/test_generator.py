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
    si_node = ListNode("SI", parent=root)
    vpsi_node = SiteNode("VPSI", parent=si_node)

    labs_node = ListNode("labs", parent=root)
    dcsl_node = SiteNode("DCSL")
    master_node = SiteNode("master")

    # settings parents which were not set above
    root.add_child(ic_node)
    ic_node.add_child(blabla_node)
    # chained setting of children
    labs_node.add_child(dcsl_node).add_child(master_node)

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

    def test_exception_on_creation(self, tree):
        with pytest.raises(ValueError):
            SiteNode("fails", parent="not a node")

    def test_full_name(self, tree):
        root, ic_node, blabla_node, vpsi_node, labs_node, dcsl_node = tree
        assert root.full_name() == ""
        assert ic_node.full_name() == "/IC"
        assert blabla_node.full_name() == "/IC/blabla"
        assert labs_node.full_name() == "/labs"
        assert vpsi_node.full_name() == "/SI/VPSI"
        assert dcsl_node.full_name() == "/labs/DCSL"
