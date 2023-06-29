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


from .RegularExpression.Graph import Graph, GraphOperator, Edge, NODE_TAG
from .RegularExpression.BaseOperator import ReorganizeGraphEdge, CopyGraph, MergeGraph, MergeEdgeAllowSet
from .RegularExpression.SpecialOperator import MakeVirtualStartNode, AddDataToEndNode
from .RegularExpression.SpecialCompute import GetStartNodes
from .RegularExpression.Function import getRandomString, dealWithConflict
from .RegularExpression.Exp2NFA import Exp2NFA
from .RegularExpression.NFA2DFA import SubsetConstruction
from .RegularExpression.SimplifyDFA import Brzozowski

from kit.MQKit import MQSever, Message, MQ_TYPE

class Lex:
    """
    中介模式，提供用户调用的主要接口
    """

    def __init__(self, raw):
        self.expr_list = []
        self.raw = raw
        self.expr_list = self.parse()
        self.graph = self.compile()

    @staticmethod
    def read_file(filename):
        with open(filename, 'r') as f:
            return f.read()

    def parse(self):
        raw = map(lambda x: x.strip(), self.raw.strip().split('\n'))
        raw = list(filter(lambda x: x, raw))
        raw = map(lambda x: x[:x.rfind('//')].strip() if x.rfind('//') != -1 and x.rfind('//') > x.rfind('"') else x, raw)
        raw = list(filter(lambda x: x, raw))

        def parse(s: str):
            pos = s.rfind(' ')
            return s[:pos].strip(), s[pos:].strip()

        return list(map(parse, raw))

    @staticmethod
    def getExpr(expr_raw: str):
        assert expr_raw.startswith('"') and expr_raw.endswith('"')
        return eval(expr_raw)

    def compile(self):
        g = Graph()
        for idx, (expr, raw) in enumerate(self.expr_list):
            expr = self.getExpr(expr)
            gt = Exp2NFA(expr).operate()  # 根据正则表达式生成图
            MQSever.publish(MQ_TYPE.Lex_Graph_Pipe, Message(f"NFA::{raw}", MergeEdgeAllowSet().operate(gt).to_json()))  # 存储NFA图
            gt = ReorganizeGraphEdge().operate(gt)  # 将图的边进行化简
            gt = SubsetConstruction(lambda a, b: a).operate(gt)  # NFA 转 DFA
            MQSever.publish(MQ_TYPE.Lex_Graph_Pipe, Message(f"DFA::{raw}", MergeEdgeAllowSet().operate(gt).to_json()))  # 存储NFA图
            gt = Brzozowski().operate(gt)  # 最简化DFA Brzozowski算法
            MQSever.publish(MQ_TYPE.Lex_Graph_Pipe, Message(f"SDFA::{raw}", MergeEdgeAllowSet().operate(gt).to_json()))  # 存储NFA图
            gt = AddDataToEndNode(raw, idx).operate(gt)  # 添加标签
            # 复制图合并到g中
            g = MergeGraph(g).operate(CopyGraph(getRandomString(5)).operate(gt))
        # print(111, g)
        g = ReorganizeGraphEdge().operate(g)
        g = MakeVirtualStartNode().operate(g)  # 添加起始虚拟节点
        g = SubsetConstruction(dealWithConflict).operate(g)  # 再进行一次 NFA 化简 DFA
        g = MergeEdgeAllowSet().operate(g)  # 最后进行一次相同边但不同allow的合并操作
        MQSever.publish(MQ_TYPE.Lex_Graph_Pipe, Message(f"SDFA", g.to_json()))  # 存储合并后的最后SDFA

        self.graph = g

        return g

    def generate_lex(self) -> (str, str):
        """
        生成词法分析程序
        :return: 词法分析程序源代码
        """
        assert self.graph is not None, "未进行compile操作"
        st_nodes = GetStartNodes().compute(self.graph)
        assert len(st_nodes) == 1
        code = ''
        st = st_nodes[0]
        edge_list = []
        state_map = {n.name: i for i, n in enumerate(self.graph.getAllNodes())}
        done = set()
        qu = [st.name]
        while qu:
            pos = qu.pop(0)
            if pos in done:
                continue
            done.add(pos)
            code += f"case {state_map[pos]}: \n"
            for e in self.graph.getOutDegree(pos):
                e: Edge
                qu.append(e.to)
                idx = len(edge_list)
                edge_list.append(e)
                code += f"if(check({idx}, c)) {{ *p++ = c; state={state_map[e.to]}; }}\nelse "
            node = self.graph.getNode(pos)
            assert node is not None
            if node.tag & NODE_TAG.START != 0:
                code += f"if(c == -1) {{ return; }}\nelse "
            if node.tag & NODE_TAG.END != 0:
                if node.data['raw'][0] == "skip":
                    code += f"{{ undoGetChar(c); p = buffer; state = 0; }}\n"
                else:
                    code += f"{{ undoGetChar(c); *p = 0; output(\"{node.data['raw'][0]}\", buffer); p = buffer; state = 0; }}\n"
            else:
                code += f"{{ undoGetChar(c); *p = 0; error(\"Lex Error\"); }}\n"
            code += "break;\n"

        array_code = "{\n"
        for i, e in enumerate(edge_list):
            array_code += self.allow_set_to_bitmap(e.allow) + ',\n'
        array_code += '}'
        return dict(code=code, array=array_code)

    @staticmethod
    def allow_set_to_bitmap(allow: set):
        ans = [0] * 16
        for c in allow:
            ans[ord(c) // 8] |= (1 << (ord(c) % 8))
        return '{' + ','.join(map(str, ans)) + '}'

    @staticmethod
    def render(**kwargs):
        from .template import template
        for k, v in kwargs.items():
            template = template.replace(f"/// {k} ///", v)
        return template

    def getLex(self):
        return self.render(**self.generate_lex())

    def saveLex(self, filename):
        code = self.getLex()
        with open(filename, 'w') as f:
            f.write(code)
