__author__ = 'kukoban'


from signal_parser.term import InteriorNode, EmptyNode, LeafNode, Term


class TreeBuilder(object):

    def build_tree(self):
        pass

    def build_interior_node(self, interior_node_label):
        pass

    def build_leaf_node(self, prev_node, leaf_node_label):
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

    def build_leaf_node(self, prev_node, leaf_node_label):
        prev_node.add_child(LeafNode(leaf_node_label))

    def build_interior_node(self, interior_node_sort):
        return InteriorNode(interior_node_sort)

    def build_dependency(self, parent_node, child_node):
        parent_node.add_child(child_node)


class XmlTreeBuilder(TreeBuilder):
    pass

class DotTreeBuilder(TreeBuilder):
    pass

