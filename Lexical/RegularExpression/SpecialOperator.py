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

from .Graph import Graph, GraphOperator, NODE_TAG, Query, Edge, Node
from .BaseOperator import MakeSameTag
from .SpecialCompute import GetStartNodes, GetEndNodes
from .Function import getHash

class MakeVirtualNode(GraphOperator):
    """
    实现创建虚拟节点操作，将节点标记为vst与ved
    """

    def operate(self, g: Graph | None = None) -> Graph:
        st_nodes = GetStartNodes().compute(g)
        ed_nodes = GetEndNodes().compute(g)

        g = MakeSameTag(NODE_TAG.NORMAL).operate(g)

        g.node('vst', NODE_TAG.START)
        g.node('ved', NODE_TAG.END)

        for n in st_nodes:
            g.edge('vst', n.name, None)
        for n in ed_nodes:
            g.edge(n.name, 'ved', None)

        return g

class MakeVirtualStartNode(GraphOperator):
    """
    实现创建虚拟节点操作，将节点标记为vst
    """

    def operate(self, g: Graph | None = None) -> Graph:
        st_nodes = GetStartNodes().compute(g)
        for n in st_nodes:
            n.tag = NODE_TAG.NORMAL
            g.updateNode(n)
        g.node('vst', NODE_TAG.START)
        for n in st_nodes:
            g.edge('vst', n.name, None)
        return g

class ReverseGraph(GraphOperator):
    """
    反转图中所有的边
    """

    def operate(self, g: Graph | None = None) -> Graph:
        new_g = Graph(g.getAllNodes())
        for e in g.getAllEdges():
            new_g.edge(e.to, e.fr, e.allow, e.data)
        return new_g

class ReverseTag(GraphOperator):
    """
    反转途中节点的标记
    Start -> End
    End -> Start
    Normal -> Normal
    """

    def operate(self, g: Graph | None = None) -> Graph:
        for n in g.getAllNodes():
            if n.tag == NODE_TAG.NORMAL:
                continue
            n.tag = bool(n.tag & NODE_TAG.START) * NODE_TAG.END + bool(n.tag & NODE_TAG.END) * NODE_TAG.START
            g.updateNode(n)
        return g

class ReachableCut(GraphOperator):
    """
    不可到达裁剪，裁剪掉所有不可到达的节点和相关联的边
    """

    def operate(self, g: Graph | None = None) -> Graph:
        st_nodes = GetStartNodes().compute(g)
        qu = [n.name for n in st_nodes]
        reachable = set()
        while qu:
            pos = qu.pop(0)
            if pos in reachable:
                continue
            reachable.add(pos)
            for e in g.getOutDegree(pos):
                qu.append(e.to)
        return Graph(
            nodes=[
                n for n in g.getAllNodes() if n.name in reachable
            ],
            edges=[
                e for e in g.getAllEdges() if e.fr in reachable and e.to in reachable
            ]
        )

class AddDataToEndNode(GraphOperator):
    """
    向图中的所有终止节点添加data数据
    """
    def __init__(self, expr='', priority=0):
        self.expr = expr
        self.priority = priority
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        for n in g.getAllNodes():
            if n.tag & NODE_TAG.END:
                n.data.update(dict(raw=(self.expr, self.priority)))
                g.updateNode(n)
        return g
