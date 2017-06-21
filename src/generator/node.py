"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""
from abc import ABCMeta, abstractclassmethod


class Node(metaclass=ABCMeta):

    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []

    @abstractclassmethod
    def run(self):
        pass


class ListNode(Node):
    def __init__(self, name):
        super().__init__(name)

    def run(self):
        pass


class RootNode(Node):
    def __init__(self, name):
        super().__init__(name)

    def run(self):
        pass


class SiteNode(Node):
    def __init__(self, name):
        super().__init__(name)

    def run(self):
        pass
