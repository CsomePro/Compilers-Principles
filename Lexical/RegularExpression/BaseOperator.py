"""
MIT License

Copyright (c) 2023 Csome陈绍民

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

from typing import List

from .Graph import Graph, GraphOperator, NODE_TAG, Query, Edge
from .Function import getHash
import hashlib



class CopyGraph(GraphOperator):
    """
    实现复制Graph对象内的所有节点和边的操作。
    >>> g = Graph()
    >>> c = CopyGraph().operate(g)
    """
    def __init__(self, padding=''):
        self.padding = padding
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        assert g is not None
        nodes = g.getAllNodes()
        edges = g.getAllEdges()
        g = Graph()
        for n in nodes:
            g.node(getHash(n.name + self.padding), n.tag, n.data)
        for e in edges:
            g.edge(getHash(e.fr + self.padding), getHash(e.to + self.padding), e.allow, e.data)
        return g


class MergeGraph(GraphOperator):
    """
    合并两个或多个复合图，将顶点和边合并到一个新的图中。
    >>> g0 = Graph()
    >>> g1 = Graph()
    >>> g2 = MergeGraph(g0).operate(g1)
    >>> id(g0) == id(g2)
    True
    """

    def __init__(self, g: Graph):
        self.g = g
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        for n in g.getAllNodes():
            self.g.node(n.name, n.tag, n.data)

        for e in g.getAllEdges():
            self.g.edge(e.fr, e.to, e.allow, e.data)

        return self.g


class MakeSameTag(GraphOperator):
    """
    将图中所有的节点设置相同的Tag
    >>> g = Graph()
    >>> g = MakeSameTag(NODE_TAG.NORMAL).operate(g)
    """
    def __init__(self, tag):
        self.tag = tag
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        g.nodes.update(dict(tag=self.tag), Query().tag != self.tag)
        return g


class ReorganizeGraphEdge(GraphOperator):
    """
    重新安排所有的边，使得任意两条边上的allow集合不会出现部分相交的情况
    >>> g = Graph()
    >>> g.node("a", NODE_TAG.NORMAL)
    >>> g.node("b", NODE_TAG.NORMAL)
    >>> g.node("c", NODE_TAG.NORMAL)
    >>> g.edges("a", "b", {"a", "b"})
    >>> g.edges("a", "c", {"a", "c"})
    >>> g = ReorganizeGraphEdge().operate(g)
    >>> g.edges.all()
    {{"fr": "a", "to": "b", "allow": {"a"}, "data": {}}, {"fr": "a", "to": "b", "allow": {"b"}, "data": {}},
    {"fr": "a", "to": "c", "allow": {"a"}, "data": {}},  {"fr": "a", "to": "c", "allow": {"c"}, "data": {}}}
    """

    def operate(self, g: Graph | None = None) -> Graph:
        edges = g.getAllEdges()
        allows = list(filter(lambda x: x, map(lambda e: e.allow, edges)))
        allows = self.divsSet(*allows)
        new_edges = []
        for e in edges:
            a = e.allow
            if a is None:
                new_edges.append(e)
                continue
            for s in allows:
                if a & s:
                    et = Edge(e.fr, e.to, s, e.data)
                    if et not in new_edges:
                        new_edges.append(et)
        return Graph(g.getAllNodes(), new_edges)

    @staticmethod
    def divsSet(*args):
        elements = set()
        for st in args:
            for e in st:
                elements.add(e)
        arr = {_: hashlib.sha256(b'zero') for _ in elements}
        for i, st in enumerate(args):
            for e in st:
                arr[e].update(str(i).encode())
        mp = {}
        for e, h in arr.items():
            hs = h.hexdigest()
            if hs not in mp:
                mp[hs] = set()
            mp[hs].add(e)
        return list(map(lambda x: x[1], mp.items()))

class MergeEdgeAllowSet(GraphOperator):
    """
    将两个节点之间的边的所有allow set进行合并
    >>> g = Graph()
    >>> g.node("a")
    >>> g.node("b")
    >>> g.edge("a", "b", {"a"})
    >>> g.edge("a", "b", {"b"})
    >>> g.getAllEdges()
    [Edge("a", "b", {"a"}, {}), Edge("a", "b", {"b"}, {})]
    >>> g = MergeEdgeAllowSet().operate(g)
    >>> g.getAllEdges()
    [Edge("a", "b", {"a", "b"}, {})]
    """

    def operate(self, g: Graph | None = None) -> Graph:
        edges_set = set([
            (e.fr, e.to) for e in g.getAllEdges()
        ])
        new_edges: List[Edge] = []
        new_none_edges: List[Edge] = []
        for et in edges_set:
            q = Query()
            for e in map(lambda x: Edge(**x), g.edges.search(q.fr == et[0] and q.to == et[1])):
                if e.allow is None:
                    new_none_edges.append(e)
                    continue
                result = list(filter(lambda x: x.fr == e.fr and x.to == e.to and x.data == e.data, new_edges))
                if result:
                    result[0].allow.update(e.allow)
                else:
                    new_edges.append(Edge(e.fr, e.to, e.allow.copy(), e.data))
        return Graph(g.getAllNodes(), new_edges + new_none_edges)
