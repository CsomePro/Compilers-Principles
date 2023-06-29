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

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Set, Dict
from .Context import Context


class _EPSILON:
    """
    空类型
    """
    def __repr__(self):
        return "@"


class _EOF:
    """
    EOF类型
    """
    def __repr__(self):
        return "$"


EPS = _EPSILON()
EOF = _EOF()


class Node(ABC):
    """
    语法树节点抽象类
    """
    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def to_json(self):
        """
        实现语法树节点序列化
        :return: 返回一个可json序列化的对象
        """
        pass

    @abstractmethod
    def simplify(self):
        """
        化简语法树节点
        :return: 返回化简后的当前节点
        """
        pass

    @abstractmethod
    def compile(self, global_c: Context, local_c: Context) -> []:
        """
        编译当前节点，生成中间代码
        :param global_c: 全局上下文
        :param local_c: 局部上下文
        :return: 返回生成的中间代码序列或者是CodeObject
        """
        pass


class InterNode(Node):
    """
    实现Node简单分析数节点
    可以实现简单的分析树构建
    """

    def compile(self, global_c: Context, local_c: Context):
        pass

    def __init__(self, name, child: [Node] = None):
        super().__init__()
        self.name = name
        if child is None:
            child = []
        self.child = child

    def to_json(self):
        pass

    def __repr__(self):
        return f"{self.name}({repr(len(self.child))})"

    def simplify(self):
        new = []
        for n in self.child:
            if isinstance(n, Node):
                new.append(n.simplify())
            else:
                new.append(n)
        if len(new) == 1:
            return new[0]
        self.child = new
        return self


class Stack:
    """
    栈数据结构实现
    """

    def __init__(self):
        self.stack = []

    def push(self, *args):
        """
        将一个或者多个元素推入栈中
        :param args: 一个元素或者多个元素列表
        :return: None
        >>> s = Stack()
        >>> s.push(1,2,3)
        >>> s.push(4,5,6)
        >>> s.pop()
        6
        """
        self.stack.extend(args)

    def pop(self) -> Any:
        """
        从栈顶弹出一个元素
        :return:  返回被弹出的的元素
        >>> s = Stack()
        >>> s.push(1,2,3)
        >>> s.push(4,5,6)
        >>> s.pop()
        6
        """
        return self.stack.pop(-1)

    def pop_list(self, n=1) -> List:
        """
        从栈顶弹出n个元素
        :param n: 要从栈顶弹出的元素个数
        :return:   返回被弹出的元素列表
        >>> s = Stack()
        >>> s.push(1,2,3)
        >>> s.push(4,5,6)
        >>> s.pop_list(2)
        [6, 5]
        """
        assert n >= 1
        return [self.pop() for _ in range(n)]

    def top(self):
        """
        查看栈顶元素
        :return: 返回被查看的栈顶元素
        >>> s = Stack()
        >>> s.push(1,2,3)
        >>> s.push(4,5,6)
        >>> s.top()
        6
        """
        return self.stack[-1]

    def view(self, n=1):
        """
        查看栈顶n个元素
        :param n: 要查看的元素个数
        :return: 返回查看的元素列表
        >>> s = Stack()
        >>> s.push(1,2,3)
        >>> s.push(4,5,6)
        >>> s.view(2)
        [6, 5]
        """
        assert n >= 1
        return self.stack[-1:-1 - n:-1]

    def __repr__(self):
        return repr(self.stack)


class Action:
    """
    动作接口
    """

    def __init__(self, name):
        self.name = name

    def run(self, stack: Stack) -> Any:
        """
        动作执行的主要函数
        :param stack: 语法树节点栈
        :return:  执行结果
        """
        pass

    def __repr__(self):
        return f"Action({repr(self.name)})"

    def __str__(self):
        return "__action__"


class GrammarParse:
    """
    文法处理接口
    """

    def compile(self) -> Grammar:
        pass


class Production:
    """
    保存产生式的结构
    """

    def __init__(self, start: str, sequence: List[str | EPS]):
        """
        接受两个参数初始化
        :param start: 产生式的起始符号
        :param sequence: 产生式的推导列表
        """
        self._start = start
        self._seq = sequence
        if not self._seq:
            self._seq.append(EPS)

    @property
    def left(self):
        """
        可以将产生式推导列表左边第一个非动作符号字符取出
        :return:  产生式的左部分
        >>> p = Production("S", ["A", "B"])
        >>> p.left
        'A'
        """
        for sym in self.seq:
            if isinstance(sym, Action):
                continue
            return sym

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, v):
        self._start = v

    @property
    def seq(self):
        return self._seq

    @seq.setter
    def seq(self, value):
        self._seq = value

    def __repr__(self):
        return f"Production({repr(self.start)}, {repr(self.seq)})"

    def __str__(self):
        return f"{self.start} ::= {' '.join(map(repr, self.seq))}"


class Grammar:
    """
    文法存储的类
    包括一个文法开符号，产生式列表、终止符号集合、非终止符号集合，first集合缓冲，follow集合缓冲
    """

    def __init__(self,
                 start: str,
                 productions: List[Production],
                 terminal: set,
                 nonterminal: set):
        self.start = start
        self.productions: List[Production] = productions
        self.terminal = terminal
        self.non_terminal = nonterminal
        self.terminal.add(EPS)
        self.first_map: Dict[str, Set[str | EOF | EPS]] | None = None
        self.follow_map: Dict[str, Set[str | EOF | EPS]] | None = None

    def clear_first_sets(self):
        self.first_map = None

    def clear_follow_sets(self):
        self.follow_map = None

    def cal_first_sets(self):
        if self.first_map is not None:
            return self.first_map

    def cal_follow_sets(self):
        if self.follow_map is not None:
            return self.follow_map

    def __repr__(self):
        return f"G[{self.start}]={{\n\tVT={self.terminal}\n\tVN={self.non_terminal}\n\t" \
               + '\n\t'.join(map(str, self.productions)) + "\n}"

# if __name__ == '__main__':
#     a = Stack()
#     a.push(*[1, 3, 4])
#     print(a.
