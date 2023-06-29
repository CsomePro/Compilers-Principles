import unittest

from Lexical.RegularExpression.Interpreter import *
from Lexical.RegularExpression.Exp2NFA import Exp2NFA


class Test_Interpreter(unittest.TestCase):

    def test_end_expr(self):
        tmp = EndExpr('v')
        g = tmp.interpret()
        self.assertIsInstance(g, Graph)
        nodes = g.getAllNodes()
        edges = g.getAllEdges()
        self.assertEqual(len(nodes), 2)
        self.assertEqual(len(edges), 1)

    def test_link_expr(self):
        tmp = LinkExpr(EndExpr('c'), EndExpr('a'))
        g = tmp.interpret()
        self.assertIsInstance(g, Graph)

    def test_or_expr(self):
        tmp = OrExpr(EndExpr('c'), EndExpr('b'))
        g = tmp.interpret()
        # print(g)

    def test_positive_closure(self):
        tmp = PositiveClosureExpr(EndExpr('c'))
        g = tmp.interpret()
        # print(g)

    def test_regex_interpret(self):
        tmp = RegexInterpret('a|bc')
        self.assertEqual(str(tmp.expr), "Or(End('a'), Link(End('b'), End('c')))")
        # tmp = RegexInterpret('(a+b)+([0-9]+)')
        # expr = tmp.compile()
        # print(expr)
        # self.assertEqual(tmp.compile(), )
        g = tmp.operate(None)
        print(g)

    def test_set_expr(self):
        tmp = SetExpr('0-1a-b')
        self.assertSetEqual(tmp.getAllowSet(), {'0', '1', 'a', 'b'})


class Test_Exp2NFA(unittest.TestCase):

    def test_operator(self):
        tmp = Exp2NFA('[a-zA-Z0-9]+', 'ID')
        g = tmp.operate(None)
        print(g)


from Lexical.RegularExpression.NFA2DFA import NFA2DFA, SubsetConstruction


class Test_NFA2DFA(unittest.TestCase):

    def test_NFA2DFA_operator(self):
        g = Exp2NFA("[0-1][2-3]+").operate()
        # print(g)
        g = ReorganizeGraphEdge().operate(g)
        print(g)
        g = NFA2DFA().operate(g)
        print(g)

    def test_subset_construction(self):
        g = Exp2NFA("[0-1][2-3]+").operate()
        # print(g)
        g = ReorganizeGraphEdge().operate(g)
        print(g)
        g = SubsetConstruction().operate(g)
        print(g)

from Lexical.RegularExpression.SimplifyDFA import Brzozowski
class Test_Simplify_DFA(unittest.TestCase):

    def test_brozozowski(self):
        g = Exp2NFA("\\[").operate()
        g = ReorganizeGraphEdge().operate(g)
        g = SubsetConstruction().operate(g)
        print(g)
        g = Brzozowski().operate(g)
        print(g)

from Lexical.RegularExpression.BaseOperator import ReorganizeGraphEdge, MergeEdgeAllowSet


class test_BaseOperator(unittest.TestCase):

    def test_reorganize_graph_edge(self):
        g = Graph([
            Node('1', 0),
            Node('2', 0),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4})
        ])
        print(g)
        g = ReorganizeGraphEdge().operate(g)
        print(g)

    def test_merge_edge_allow_set(self):
        g = Graph([
            Node('1', 0),
            Node('2', 0),
            Node('3', 0),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4}),
            Edge('2', '3', allow={2, 3, 4})
        ])
        print(g)
        g = MergeEdgeAllowSet().operate(g)
        print(g)


from Lexical.RegularExpression.SpecialOperator import MakeVirtualNode, ReverseGraph, ReachableCut, ReverseTag
from Lexical.RegularExpression.Graph import NODE_TAG


class Test_special_operator(unittest.TestCase):

    def test_make_virtual_node(self):
        g = Graph([
            Node('1', NODE_TAG.START),
            Node('2', NODE_TAG.START | NODE_TAG.END),
            Node('3', NODE_TAG.START),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4}),
            Edge('2', '3', allow={2, 3, 4})
        ])
        print(g)
        g = MakeVirtualNode().operate(g)
        print(g)

    def test_reverse_graph(self):
        g = Graph([
            Node('1', NODE_TAG.START),
            Node('2', NODE_TAG.START | NODE_TAG.END),
            Node('3', NODE_TAG.START),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4}),
            Edge('2', '3', allow={2, 3, 4})
        ])
        print(ReverseGraph().operate(g))

    def test_reachable_cut(self):
        g = Graph([
            Node('1', NODE_TAG.START),
            Node('2', NODE_TAG.END),
            Node('3', NODE_TAG.NORMAL),
            Node('4', NODE_TAG.NORMAL),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4}),
            Edge('2', '3', allow={2, 3, 4}),
            Edge('4', '3', allow={2, 3, 4}),
        ])
        print(ReachableCut().operate(g))

    def test_reverse_tag(self):
        g = Graph([
            Node('1', NODE_TAG.START | NODE_TAG.END),
            Node('2', NODE_TAG.END),
            Node('3', NODE_TAG.NORMAL),
            Node('4', NODE_TAG.NORMAL),
        ], [
            Edge('1', '2', allow={1, 2, 3}),
            Edge('1', '2', allow={2, 3, 4}),
            Edge('2', '3', allow={2, 3, 4}),
            Edge('4', '3', allow={2, 3, 4}),
        ])
        print(ReverseTag().operate(g))


if __name__ == '__main__':
    unittest.main()
