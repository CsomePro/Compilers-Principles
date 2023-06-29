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

from typing import Tuple, List

from .Error import RegexCompileError
# language: python3
# 中文注释

from .Graph import GraphOperator, Graph, Node, Edge, NODE_TAG
from abc import ABC, abstractmethod
from .BaseOperator import CopyGraph, MergeGraph, MakeSameTag
import random

LETTER = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def getRandomString(k=4):
    return ''.join(random.choices(LETTER, k=k))


def copyGraphValid(g):
    padding = getRandomString(5)
    g = CopyGraph(padding).operate(g)
    # 复制图并消除节点编号重复
    # 判断是否为空列表否则取出第0项赋值给st
    st_node = g.queryNodes(tag=NODE_TAG.START)[0]
    ed_node = g.queryNodes(tag=NODE_TAG.END)[0]
    st_node.tag = NODE_TAG.NORMAL
    ed_node.tag = NODE_TAG.NORMAL
    g.updateNode(st_node)
    g.updateNode(ed_node)
    st, ed = st_node.name, ed_node.name
    assert st is not None and ed is not None, '图错误'
    return st, ed, g


class Expression(ABC):

    @abstractmethod
    def interpret(self) -> Graph:
        pass

    @abstractmethod
    def __repr__(self):
        pass


# 正则表达式终结符node
class EndExpr(Expression):
    def __init__(self, exp: str):
        assert len(exp) == 1, f"只允许一个字符: {exp}"
        self.exp = exp
        super().__init__()

    def interpret(self) -> Graph:
        return Graph(
            nodes=[Node('st', NODE_TAG.START), Node('ed', NODE_TAG.END)],
            edges=[Edge('st', 'ed', allow=set(self.exp))]
        )

    def __repr__(self):
        return f"End('{self.exp}')"


# 处理正则表达式中[exp]的操作
class SetExpr(Expression):

    def __init__(self, exp: str):
        self.exp = exp
        self.pos = -1
        self.tokenList = self.makeTokenList()
        self.tokenPos = -1
        self.allow_set = self.statement()

    def interpret(self) -> Graph:
        return Graph(
            nodes=[Node('st', NODE_TAG.START), Node('ed', NODE_TAG.END)],
            edges=[Edge('st', 'ed', allow=set(self.allow_set))]
        )

    def getNextToken(self) -> Tuple[str, str]:
        """
        取出下一个token
        :return: (token类别， 源expr值)
        """
        self.pos += 1
        if self.pos >= len(self.exp):
            return 'EOF', ''
        if self.exp[self.pos] == '\\':
            self.pos += 1
            assert self.pos < len(self.exp), f"\\ needs more chars: {self.exp}"
            return 'CHAR', self.exp[self.pos]
        elif self.exp[self.pos] == '-':
            return 'LINK', '-'
        else:
            return 'CHAR', self.exp[self.pos]

    def makeTokenList(self) -> List:
        ans = []
        while True:
            t, c = self.getNextToken()
            ans.append((t, c))
            if t == 'EOF':
                break
        return ans

    def getToken(self):
        self.tokenPos += 1
        return self.tokenList[self.tokenPos]

    def getExtraToken(self):
        return self.tokenList[self.tokenPos + 1]

    """
    statement :
        base-expr statement | base-expr
    base-expr :
        CHAR '-' CHAR | CHAR
    """

    def base_expr(self) -> set:
        t, c0 = self.getToken()
        assert t == 'CHAR', f'{t} {c0} is not a valid token: CHAR'
        t, c = self.getExtraToken()
        if t != 'LINK':
            return {c0}
        t, c = self.getToken()
        assert t == 'LINK', f'{t}'
        t, c1 = self.getToken()
        assert t == 'CHAR', f'{t} {c1} is not a valid token: CHAR'
        ans = set()
        for c in range(ord(c0), ord(c1) + 1):
            ans.add(chr(c))
        return ans

    def statement(self):
        ans = set()
        while self.tokenPos + 1 < len(self.tokenList):
            t, c = self.getExtraToken()
            if t == 'EOF':
                break
            assert t == 'CHAR', f'{t} {c} is not a valid token: CHAR'
            ans = ans | self.base_expr()
        return ans

    def getAllowSet(self):
        return self.allow_set

    def __repr__(self):
        return f"Set('{self.exp}')"


class ClosureExpr(Expression):
    """
    解决正则表达式闭包的处理
    exp* :
        st->G(exp)->ed
        st->ed
        G(exp).ed->G(exp).st
    """

    def __init__(self, expr: Expression):
        self.expr = expr

    def interpret(self) -> Graph:
        g: Graph = self.expr.interpret()
        st, ed, g = copyGraphValid(g)
        g.node('st', NODE_TAG.START)
        g.node('ed', NODE_TAG.END)

        g.edge(ed, st, allow=None)  # G(exp).ed->G(exp).st
        g.edge('st', st, allow=None)  # st->G(exp)
        g.edge(ed, 'ed', allow=None)  # G(exp)->ed
        g.edge('st', 'ed', allow=None)  # G(exp)->ed
        return g

    def __repr__(self):
        return f"Closure({self.expr})"


class OptionExpr(Expression):
    """
    正则表达式可选操作
    expr? :
        st->G(expr)->ed
        st->ed
    """

    def __init__(self, expr: Expression):
        self.expr = expr

    def interpret(self) -> Graph:
        g = self.expr.interpret()
        st, ed, g = copyGraphValid(g)
        g.node('st', NODE_TAG.START)
        g.node('ed', NODE_TAG.END)
        g.edge('st', 'ed', allow=None)  # st -> ed
        g.edge('st', st, allow=None)  # st -> G(expr)
        g.edge(ed, 'ed', allow=None)  # ed -> G(expr)
        return g

    def __repr__(self):
        return f"Option({self.expr})"


class LinkExpr(Expression):
    """
    正则表达式链接操作
    expr1expr2 :
        st->G(expr1)->G(expr2)->ed
    """

    def __init__(self, left_expr: Expression, right_expr: Expression):
        self.left = left_expr
        self.right = right_expr

    def interpret(self) -> Graph:
        gl = self.left.interpret()
        gr = self.right.interpret()
        lst, led, gl = copyGraphValid(gl)
        rst, red, gr = copyGraphValid(gr)
        g = MergeGraph(gl).operate(gr)

        g = MakeSameTag(NODE_TAG.NORMAL).operate(g)

        g.node('st', NODE_TAG.START)
        g.node('ed', NODE_TAG.END)

        g.edge('st', lst, allow=None)  # st->G(expr1)
        g.edge(led, rst, allow=None)   # G(expr1)->G(expr2)
        g.edge(red, 'ed', allow=None)  # G(expr2)->ed

        return g

    def __repr__(self):
        return f"Link({self.left}, {self.right})"


class OrExpr(Expression):
    """
    处理正则表达式中的或操作
    expr1|expr2 :
        st->G(expr1)->ed
        st->G(expr2)->ed
    """

    def __init__(self, left_expr: Expression, right_expr: Expression):
        self.left = left_expr
        self.right = right_expr

    def interpret(self) -> Graph:
        gl = self.left.interpret()
        gr = self.right.interpret()
        lst, led, gl = copyGraphValid(gl)
        rst, red, gr = copyGraphValid(gr)
        g = MergeGraph(gl).operate(gr)

        g = MakeSameTag(NODE_TAG.NORMAL).operate(g)

        g.node('st', NODE_TAG.START)
        g.node('ed', NODE_TAG.END)

        g.edge('st', lst, allow=None)  # st->G(expr1)
        g.edge(led, 'ed', allow=None)  # G(expr1)->ed
        g.edge('st', rst, allow=None)  # st->G(expr2)
        g.edge(red, 'ed', allow=None)  # G(expr2)->ed

        return g

    def __repr__(self):
        return f"Or({self.left}, {self.right})"


class PositiveClosureExpr(Expression):
    """
    正闭包正则表达式
    expr+ :
        st->G1(expr)->mid->G2(expr)->ed
        G2(expr).ed->G2(expr).st
        mid->ed
    """

    def __init__(self, expr: Expression):
        self.expr = expr

    def interpret(self) -> Graph:
        g: Graph = self.expr.interpret()
        st1, ed1, g1 = copyGraphValid(g)
        st2, ed2, g2 = copyGraphValid(g)

        g = MergeGraph(g1).operate(g2)

        g.node('st', NODE_TAG.START)
        g.node('mid', NODE_TAG.NORMAL)
        g.node('ed', NODE_TAG.END)

        g.edge('st', st1, allow=None)       # st->G1(expr)
        g.edge(ed1, 'mid', allow=None)      # G1(expr)->mid
        g.edge('mid', st2, allow=None)      # mid->G2(expr)
        g.edge(ed2, 'ed', allow=None)       # G2(expr)->ed

        g.edge(ed2, st2, allow=None)        # G2(expr).ed->G2(expr).st
        g.edge('mid', 'ed', allow=None)     # mid->ed

        return g

    def __repr__(self):
        return f"Positive({self.expr})"


# 正则表达式解释器，使用解释器模式设计
class RegexInterpret(GraphOperator):
    """
    正则表达式文法
    expr :
        term '|' expr | term
    term :
        stmt term | stmt
    stmt
        : factor '*'
        | factor '+'
        | factor '?'
        | factor
    factor
        : '(' expr ')'
        | base

    base :
        CHAR | SET
    CHAR:
        -- ascii
    SET:
        '[' CHAR* ']'

    正则表达式词法
    \[.+\] SET
    + POSITIVE
    * CLOSURE
    ( LP
    ) RP
    | OR
    ? OPT
    . CHAR

    Token数据结构
    (TokenType, Raw, Lineno)
    """

    @staticmethod
    def raise_error(token, raw, lineno):
        raise RegexCompileError(f'正则表达式编译失败 -> {lineno} : "{raw}"({token})')

    def grammar_expr(self) -> Expression:
        token, raw, lineno = self.getExtraToken()
        if token not in ('SET', 'CHAR', 'LP'):
            self.raise_error(token, raw, lineno)
        expr0 = self.grammar_term()

        token, raw, lineno = self.getExtraToken()
        if token not in ('OR', 'EOF', 'RP'):
            self.raise_error(token, raw, lineno)
        if token == 'OR':
            self.getToken()
            expr1 = self.grammar_expr()
            return OrExpr(expr0, expr1)
        elif token == 'EOF':
            return expr0
        elif token == 'RP':
            return expr0

    def grammar_term(self) -> Expression:
        token, raw, lineno = self.getExtraToken()
        if token not in ('SET', 'CHAR', 'LP'):
            self.raise_error(token, raw, lineno)
        expr0 = self.grammar_stmt()

        token, raw, lineno = self.getExtraToken()
        if token not in ('OR', 'EOF', 'SET', 'CHAR', 'LP', 'RP'):
            self.raise_error(token, raw, lineno)
        if token in ('OR', 'EOF', 'RP'):
            return expr0
        else:
            expr1 = self.grammar_term()
            return LinkExpr(expr0, expr1)

    def grammar_stmt(self) -> Expression:
        token, raw, lineno = self.getExtraToken()
        if token not in ('SET', 'CHAR', 'LP'):
            self.raise_error(token, raw, lineno)
        expr0 = self.grammar_factor()
        token, raw, lineno = self.getExtraToken()
        if token not in ('POSITIVE', 'CLOSURE', 'RP', 'EOF', 'OPT', 'OR', 'SET', 'CHAR', 'LP'):
            self.raise_error(token, raw, lineno)
        if token == 'POSITIVE':
            self.getToken()
            return PositiveClosureExpr(expr0)
        elif token in ('RP', 'EOF', 'OR', 'SET', 'CHAR', 'LP'):
            return expr0
        elif token == 'OPT':
            self.getToken()
            return OptionExpr(expr0)
        else:
            self.getToken()
            return ClosureExpr(expr0)

    def grammar_factor(self) -> Expression:
        token, raw, lineno = self.getExtraToken()
        if token not in ('SET', 'CHAR', 'LP'):
            self.raise_error(token, raw, lineno)
        token, raw, lineno = self.getToken()
        if token == 'LP':
            expr0 = self.grammar_expr()
            token, raw, lineno = self.getToken()
            if token != 'RP':
                self.raise_error(token, raw, lineno)
            return expr0
        elif token == 'CHAR':
            return EndExpr(raw)
        else:
            return SetExpr(raw)

    def compile(self):
        self.pos = -1
        return self.grammar_expr()

    def __init__(self, statement):
        self.statement = statement
        self.tokens = self.parse()
        self.pos = -1
        self.expr = self.compile()
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        """
        处理函数，根据statement编写正则表达式解释器
        :type g: 输入需要处理的图
        """
        return self.expr.interpret()

    def parse(self) -> List:

        pos = -1
        expr = self.statement

        def getNextToken():
            nonlocal pos
            pos += 1
            if pos >= len(expr):
                return 'EOF', '', -1
            if expr[pos] == '[':
                cache = ''
                pos += 1
                while expr[pos] != ']':
                    cache += expr[pos]
                    pos += 1
                return 'SET', cache, pos
            elif expr[pos] == '*':
                return 'CLOSURE', expr[pos], pos
            elif expr[pos] == '+':
                return 'POSITIVE', expr[pos], pos
            elif expr[pos] == '|':
                return 'OR', expr[pos], pos
            elif expr[pos] == '(':
                return 'LP', expr[pos], pos
            elif expr[pos] == ')':
                return 'RP', expr[pos], pos
            elif expr[pos] == '?':
                return 'OPT', expr[pos], pos
            elif expr[pos] == "\\":
                pos += 1
                return 'CHAR', expr[pos], pos
            else:
                return 'CHAR', expr[pos], pos

        tokens = []
        while True:
            t, c, *_ = getNextToken()
            tokens.append((t, c, *_))
            if t == 'EOF':
                break
        return tokens

    def getExtraToken(self) -> Tuple[str, str, int]:
        return self.tokens[self.pos + 1]

    def getToken(self) -> Tuple[str, str, int]:
        self.pos += 1
        return self.tokens[self.pos]

# if __name__ == '__main__':
#     # print(string.printable)
#     # tc = SetExpr('0-9a-z')
#     # ta = tc.getAllowSet()
#     # print(ta, len(ta))
#     # tc = OptionExpr(EndExpr('c'))
#     # print(tc.interpret())
#
#     tc = LinkExpr(EndExpr('c'), EndExpr('b'))
#     print(tc.interpret())
