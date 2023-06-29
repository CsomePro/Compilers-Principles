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

from .Function import getHash
from .Graph import Graph, GraphOperator, NODE_TAG, Edge
from .BaseOperator import MergeEdgeAllowSet, ReorganizeGraphEdge
from .SpecialCompute import GetStartNodes, GetEndNodes
from .Error import SubsetConstructionError

class NFA2DFA(GraphOperator):
    """
    NFA图转DFA图
    """

    def operate(self, g: Graph | None = None) -> Graph:
        nodes = g.getAllNodes()
        edges = g.getAllEdges()
        st_node = g.queryNodes(tag=NODE_TAG.START)[0]
        ed_node = g.queryNodes(tag=NODE_TAG.END)[0]

        def none_closure(n: str, already=()):
            q = []
            ans = set(already)
            q.append(n)
            while q:
                p = q.pop(0)
                ans.add(p)
                for e in g.getOutDegree(p):
                    if e.allow is None and e.to not in ans:
                        q.append(e.to)
            return tuple(sorted(ans))

        print(none_closure(st_node.name))
        qu = []
        mp = {}  # set序列化后对应新的节点名称
        all_allow_set = list(filter(lambda x: x, map(lambda e: e.allow, edges)))
        qu.append((st_node.name,))
        while qu:
            node_set = qu.pop(0)
            none_closure_set = ()
            for n in node_set:
                none_closure_set = none_closure(n, none_closure_set)
            if none_closure_set in mp:
                continue
            mp[none_closure_set] = getHash(''.join(none_closure_set))

            for allow in all_allow_set:
                next_node_set = set()
                for n in none_closure_set:
                    next_node_set.update(map(lambda x: x.to, filter(lambda x: x.allow == allow, g.getOutDegree(n))))
                if next_node_set:
                    qu.append(next_node_set)

        new_mp = {}
        for k, v in mp.items():
            for kk in k:
                if kk in new_mp:
                    new_mp[kk].add(v)
                else:
                    new_mp[kk] = {v}

        new_g = Graph()
        for old_set, new_name in mp.items():
            tag = NODE_TAG.NORMAL
            data = {}
            for n in old_set:
                nt = g.getNode(n)
                tag |= nt.tag
                assert not data.keys() & nt.data.keys(), "存在合并问题"
                data.update(nt.data)
            new_g.node(new_name, tag, data)

        # print(new_g)
        # print(mp)
        # print(new_mp)
        for e in edges:
            if e.allow is None:
                continue
            for efr in new_mp[e.fr]:
                for eto in new_mp[e.to]:
                    new_g.edge(efr, eto, e.allow, e.data)
        # print(new_g)
        new_g = MergeEdgeAllowSet().operate(new_g)
        new_g = ReorganizeGraphEdge().operate(new_g)

        return new_g


class SubsetConstruction(GraphOperator):
    """
    实现NFA转DFA的SubsetConstruction算法
    参考 https://www.cnblogs.com/zzzcode/p/10843983.html
    """

    def __init__(self, conflict_callback=None):
        self.conflict_callback = conflict_callback
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:

        edges = g.getAllEdges()
        st_nodes = GetStartNodes().compute(g)
        all_allow_set = list(filter(lambda x: x, map(lambda e: ''.join(sorted(e.allow)) if e.allow else None, edges)))

        def none_closure(ns=()):
            # 求空闭包的函数传入需要求的节点
            q = []
            ans = set()
            q.extend(ns)
            while q:
                p = q.pop(0)
                ans.add(p)
                for e in g.getOutDegree(p):
                    if e.allow is None and e.to not in ans:
                        q.append(e.to)
            return frozenset(ans)

        qu = [none_closure([n.name for n in st_nodes])]
        mp = {}
        done = set()
        dtran = set()
        while qu:  # 如果还存在没有标记过的
            T = qu.pop(0)
            t_name = getHash(''.join(sorted(T)))  # 使用哈希优化
            mp[T] = t_name
            done.add(t_name)
            for allow in all_allow_set:
                next_node_set = set()
                for n in T:
                    # 获得allow set相同的所有出度节点
                    next_node_set.update(map(lambda x: x.to,
                                             filter(lambda x: ''.join(sorted(x.allow)) == allow if x.allow else x.allow == allow,
                                                    g.getOutDegree(n))))
                next_node_set = frozenset(next_node_set)
                if not next_node_set:
                    continue
                next_node_set = none_closure(next_node_set)
                next_node_set_name = getHash(''.join(sorted(next_node_set)))
                if next_node_set_name not in done:
                    qu.append(next_node_set)
                    done.add(next_node_set_name)
                dtran.add((
                    t_name,
                    next_node_set_name,
                    frozenset(allow)
                ))
        new_g = Graph()
        for old_set, new_name in mp.items():
            tag = NODE_TAG.NORMAL
            data = {}
            for n in old_set:
                nt = g.getNode(n)
                tag |= nt.tag
                if data.keys() & nt.data.keys():
                    # 当两个节点都可以在当前位置终止的时候，存在二义性，这里采用模板方法，导入一个callback函数解决
                    if self.conflict_callback is None:
                        raise SubsetConstructionError("合并出错，存在二义性")
                    data = self.conflict_callback(data, nt.data)
                else:
                    data.update(nt.data)
            new_g.node(new_name, tag, data)

        # print(mp)
        # print(dtran)
        for fr, to, allow in dtran:
            new_g.edge(fr, to, set(allow))

        new_g = MergeEdgeAllowSet().operate(new_g)
        new_g = ReorganizeGraphEdge().operate(new_g)

        return new_g





