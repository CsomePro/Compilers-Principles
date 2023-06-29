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

from typing import List, Any

from .Graph import Graph, GraphOperator, NODE_TAG, Query, Edge, Node, GraphCompute

class GetStartNodes(GraphCompute):
    """
    获得图内所有起始节点
    """

    def compute(self, g: Graph) -> List[Node]:
        q = Query()
        st_nodes = [Node(**_) for _ in
                    g.nodes.search((q.tag == NODE_TAG.START | NODE_TAG.END) | (q.tag == NODE_TAG.START))]
        return st_nodes


class GetEndNodes(GraphCompute):
    """
    获得图内所有终止节点
    """

    def compute(self, g: Graph) -> List[Node]:
        q = Query()
        ed_nodes = [Node(**_) for _ in
                    g.nodes.search((q.tag == NODE_TAG.START | NODE_TAG.END) | (q.tag == NODE_TAG.END))]
        return ed_nodes
