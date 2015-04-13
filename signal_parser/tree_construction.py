__author__ = 'kukoban'


from signal_parser.term import InteriorNode, EmptyNode, LeafNode, Term
import pydot
from xml.dom.minidom import getDOMImplementation


class TreeBuilder(object):

    def build_tree(self):
        pass

    def build_interior_node(self, interior_node_label):
        pass

    def build_leaf_node(self, prev_node, leaf_node_token):
        pass

    def build_empty_node(self, prev_node):
        pass

    def build_dependency(self, parent_node, child_node):
        pass

    def get_tree(self):
        pass


class StandardTreeBuilder(TreeBuilder):

    def __init__(self):
        super(StandardTreeBuilder, self).__init__()
        self._imagine_root = None

    def build_tree(self):
        self._imagine_root = InteriorNode('')
        return self._imagine_root

    def get_tree(self):
        return Term(self._imagine_root.children()[0])

    def build_empty_node(self, prev_node):
        prev_node.add_child(EmptyNode())

    def build_leaf_node(self, prev_node, leaf_node_token):
        prev_node.add_child(LeafNode(leaf_node_token))

    def build_interior_node(self, interior_node_sort):
        return InteriorNode(interior_node_sort)

    def build_dependency(self, parent_node, child_node):
        parent_node.add_child(child_node)


class XmlTreeBuilder(TreeBuilder):

    def __init__(self):
        super(XmlTreeBuilder, self).__init__()
        self._doc = None

    def build_tree(self):
        self._doc = None

    def get_tree(self):
        return self._doc

    def build_dependency(self, parent_node, child_node):
        if parent_node is not None:
            parent_node.appendChild(child_node)

    def build_leaf_node(self, prev_node, leaf_node_token):
        prev_node.appendChild(self._doc.createTextNode(leaf_node_token.label()))

    def build_interior_node(self, interior_node_label):
        if self._doc is None:
            self._doc = getDOMImplementation().createDocument(None, interior_node_label, None)
            return self._doc.documentElement
        else:
            return self._doc.createElement(interior_node_label)


class DotTreeBuilder(TreeBuilder):

    def __init__(self):
        super(DotTreeBuilder, self).__init__()
        self._index = 0
        self._dot = pydot.Dot(graph_type='graph')

    def build_tree(self):
        return None

    def build_interior_node(self, interior_node_label):
        self._index += 1
        return pydot.Node(self._index, label=interior_node_label)

    def build_leaf_node(self, prev_node, leaf_node_token):
        self._index += 1
        leaf_node = pydot.Node(self._index, label=leaf_node_token.label())
        self.build_dependency(prev_node, leaf_node)

    def build_empty_node(self, prev_node):
        self.build_leaf_node(prev_node, EmptyNode())

    def build_dependency(self, parent_node, child_node):
        if parent_node:
            self._dot.add_node(parent_node)
            self._dot.add_node(child_node)
            edge = pydot.Edge(parent_node, child_node)
            self._dot.add_edge(edge)

    def get_tree(self):
        return self._dot