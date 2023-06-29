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

from .Function import getHash, dealWithConflict
from .Graph import Graph, GraphOperator, NODE_TAG, Edge
from .BaseOperator import MergeEdgeAllowSet, ReorganizeGraphEdge
from .SpecialOperator import MakeVirtualNode, ReverseGraph, ReachableCut, ReverseTag
from .NFA2DFA import SubsetConstruction

class Brzozowski(GraphOperator):
    """
    使用Brzozowski算法最小化DFA
    """

    def operate(self, g: Graph | None = None) -> Graph:
        g = MakeVirtualNode().operate(g)  # 添加虚拟开始结束节点
        g = ReverseGraph().operate(g)  # 反转所有的边
        g = ReverseTag().operate(g)  # 反转开始结束节点tag
        g = SubsetConstruction(dealWithConflict).operate(g)  # SC操作化简成DFA
        g = ReachableCut().operate(g)  # 删除不可达节点

        g = MakeVirtualNode().operate(g)  # 添加虚拟开始结束节点
        g = ReverseGraph().operate(g)  # 反转所有的边
        g = ReverseTag().operate(g)  # 反转开始结束节点tag
        g = SubsetConstruction(dealWithConflict).operate(g)  # SC操作化简成DFA
        g = ReachableCut().operate(g)  # 删除不可达节点

        g = MergeEdgeAllowSet().operate(g)
        g = ReorganizeGraphEdge().operate(g)

        return g



