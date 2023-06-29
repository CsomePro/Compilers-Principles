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

import json
from typing import List, Dict, Set, Any
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from .Function import Set2Expr

# import uuid

# def getUuid(s):
#     return uuid.uuid3(uuid.UUID('87ecbf7f-bfbc-4986-81be-861eb65de874'), s)

class NODE_TAG:
    """
    节点tag类型
    """
    START = 1  # 当前节点是Start类型
    END = 2  # 当前节点是End类型
    NORMAL = 0  # 当前节点是Normal类型


class Node:
    """
    图Node节点抽象类
    """

    def __init__(self, name, tag, data=None):
        if data is None:
            data = {}
        self._name = name
        self._data = data
        self._tag = tag

    @property
    def data(self) -> dict:
        return self._data

    @property
    def name(self) -> str:
        return self._name

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def __repr__(self):
        return "Node(%r, %r, %r)" % (self.name, self.tag, self.data)


class Edge:
    """
    边节点抽象类
    """
    def __init__(self, fr, to, allow, data=None):
        if data is None:
            data = {}
        self._fr = fr
        self._to = to
        self._allow = allow
        self._data = data

    @property
    def allow(self) -> set:
        return self._allow

    @property
    def fr(self) -> str:
        if isinstance(self._fr, Node):
            return self._fr.name
        return self._fr

    @property
    def to(self) -> str:
        if isinstance(self._to, Node):
            return self._to.name
        return self._to

    @property
    def data(self) -> Dict:
        return self._data

    def __repr__(self):
        return "Edge(%r, %r, %r, %r)" % (self.fr, self.to, self.allow, self.data)

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        if self.fr == other.fr and self.to == other.to and self.allow == other.allow and self.data == other.data:
            return True
        return False


class Graph:
    """ 采用点边法存储图 """

    def __init__(self, nodes=None, edges=None):
        self.edges = TinyDB(storage=MemoryStorage)
        """
            fr: string
            to: string
            allow: set
            data: dict
        """
        self.nodes = TinyDB(storage=MemoryStorage)
        """
            name: string
            data: dict
        """
        if nodes is None:
            nodes: List[Node] = []
        if edges is None:
            edges: List[Edge] = []
        for n in nodes:
            self.node(n.name, n.tag, n.data)
        for e in edges:
            self.edge(e.fr, e.to, e.allow, e.data)

    def node(self, name: str, tag: int, data=None):
        """
        通过节点名字、tag、data创建节点
        :param name: 节点唯一名称
        :param tag: 节点tag
        :param data: 节点需要保存的data
        :return: None
        >>>  g = Graph()
        >>> g.node("a", 1)
        >>> g.node("b", 2)
        >>> g.node("c", 3)
        >>> g.nodes.all()
        [{'name': 'a', 'tag': 1, 'data': {}}
         {'name': 'b', 'tag': 2, 'data': {}}
         {'name': 'c', 'tag': 3, 'data': {}}]
        """
        if data is None:
            data = {}
        assert len(self.nodes.search(Query().name == name)) == 0, "已存在此名字节点"
        self.nodes.insert(dict(
            name=name,
            tag=tag,
            data=data,
        ))

    def edge(self, fr: str, to: str, allow: set | None, data=None):
        """
        创建边
        :param fr: 起始节点名称
        :param to: 终止节点名称
        :param allow: 允许通过的字符集合
        :param data: 边上需要存储的数据
        :return: None
        >>> g = Graph()
        >>> g.node("a")
        >>> g.node("b")
        >>> g.node("c")
        >>> g.edge("a", "b", allow={'b'})
        >>> g.edge("b", "c", allow={'a'})
        >>> g.edges.all()
        [{'fr': 'a', 'to': 'b', 'allow': {'b'},'data': {}}
         {'fr': 'b', 'to': 'c', 'allow': {'a'}, 'data': {}}]
        """
        if data is None:
            data = {}
        assert len(self.nodes.search(Query().name == fr)) == 1, f"不存在此名字节点 {fr}"
        assert len(self.nodes.search(Query().name == to)) == 1, f"不存在此名字节点 {to}"
        self.edges.insert(dict(
            fr=fr, to=to,
            allow=allow,
            data=data
        ))

    def getOutDegree(self, name: str) -> List:
        """
        可以根据名称节点名称获得所有的出度
        :param name:  要获取出度的节点名称
        :return: 出度列表
        """
        return [Edge(**_) for _ in self.edges.search(Query().fr == name)]

    def getInDegree(self, name: str) -> List:
        """
        根据节点名称获得所有的入度
        :param name: 要获取入度的节点名称
        :return: 入度列表
        """
        return [Edge(**_) for _ in self.edges.search(Query().to == name)]

    def getAllNodes(self) -> List[Node]:
        """
        获得所有节点
        :return: 所有节点
        """
        return [Node(**_) for _ in self.nodes.all()]

    def getAllEdges(self) -> List[Edge]:
        """
        获得所有边
        :return: 所有边
        """
        return [Edge(**_) for _ in self.edges.all()]

    def getNode(self, name: str) -> Node:
        """
        根据名称获得节点对象
        :param name: 要获取的节点名称
        :return: 节点对象
        """
        ans = self.nodes.get(Query().name == name)
        assert ans is not None, f"不存在name为 {name} 的节点"
        return Node(**ans)

    def queryEdges(self, **kwargs) -> List[Edge]:
        assert len(kwargs) == 1
        v: str
        k, v = next(iter(kwargs.items()))
        return [Edge(**_) for _ in self.edges.search(Query()[k] == v)]

    def queryNodes(self, **kwargs) -> List[Node]:
        assert len(kwargs) == 1
        v: str
        k, v = next(iter(kwargs.items()))
        return [Node(**_) for _ in self.nodes.search(Query()[k] == v)]

    def updateNode(self, node: Node):
        assert len(self.nodes.search(Query().name == node.name)) == 1, f"此节点不存在 {node.name}"
        self.nodes.update(dict(
            tag=node.tag,
            data=node.data,
        ), Query().name == node.name)

    def deleteNode(self, name: str):
        self.nodes.remove(Query().name == name)

    def __repr__(self):
        s = "\n".join(map(lambda n: f"{n.name} ({n.tag}) : {n.data}", self.getAllNodes())) + '\n'
        s += "\n".join(map(lambda e: f"{e.fr}->{e.to} ({Set2Expr(e.allow) if e.allow else e.allow}) : {e.data}", self.getAllEdges())) + '\n'
        return s

    def to_json(self) -> str:
        """
        将节点和边数据转换为JSON字符串
        :return: JSON字符串
        """
        return json.dumps({
            "nodes": [_ for _ in self.nodes.all()],
            "edges": [{
                "fr": _['fr'],
                "to": _['to'],
                "allow": Set2Expr(_['allow']) if _['allow'] else _['allow'],
                "data": _['data'],
            } for _ in self.edges.all()]
        })


class GraphOperator:
    """
    基本操作类，基础的 Graph 操作类
    """

    def __init__(self):
        pass

    def operate(self, g: Graph | None = None) -> Graph:
        pass


class GraphCompute:
    """
    基本操作类，基本的 Graph 计算类
    """

    def __init__(self):
        pass

    def compute(self, g: Graph) -> Any:
        pass


if __name__ == '__main__':
    a = Node('111', dict(tag=11))
    print(a.data)
    a.data.update(tag=22)
    print(a.data)
