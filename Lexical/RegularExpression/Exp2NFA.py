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

from .Graph import GraphOperator, Graph, NODE_TAG
from .Error import RegularExpressionException
from .Interpreter import RegexInterpret


class Exp2NFA(GraphOperator):
    """
    正则表达式转NFA图
    输入正则表达式和对应的tag，生成NFA图返回

    用法如下
    ```python
    >>> from Lexical.RegularExpression.Exp2NFA import Exp2NFA
    >>> g = Exp2NFA('a+', 'TEST').operate()
    >>> print(g)
    1cd98558b3 (2) : {}
    7dabfe5f1a (2) : {}
    242a2d24e4 (2) : {}
    e0e29d5054 (2) : {}
    st (0) : {}
    mid (2) : {}
    ed (1) : {'raw': 'TEST'}
    1cd98558b3->7dabfe5f1a : {'allow': {'a'}}
    242a2d24e4->e0e29d5054 : {'allow': {'a'}}
    st->1cd98558b3 : {'allow': None}
    7dabfe5f1a->mid : {'allow': None}
    mid->242a2d24e4 : {'allow': None}
    e0e29d5054->ed : {'allow': None}
    e0e29d5054->242a2d24e4 : {'allow': None}
    mid->ed : {'allow': None}
    ```
    """

    def __init__(self, exp=""):
        self.exp = exp
        if self.exp == "" or not self.exp:
            raise RegularExpressionException("正则表达式不能为空")
        super().__init__()

    def operate(self, g: Graph | None = None) -> Graph:
        g = RegexInterpret(self.exp).operate(None)
        return g
