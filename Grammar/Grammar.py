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

import os
import re
import types
from typing import Dict, List, Tuple, Any

from .Base import EPS, EOF, Grammar, Production, Action, Stack, InterNode, Node, GrammarParse, _EPSILON, _EOF
from .Error import FileGrammarParseException, GrammarException
from .Context import Context
import random
import hashlib
from kit.MQKit import MQSever, MQ_TYPE, Message

LETTER = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def getHash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:10]


def getRandomString(k=4):
    return ''.join(random.choices(LETTER, k=k))


class LL1InterAction(Action):
    def __init__(self, name, n):
        super().__init__(name)
        self.n = n

    def run(self, stack: Stack) -> Node:
        return InterNode(name=self.name, child=stack.pop_list(self.n)[::-1])

    def __repr__(self):
        return f"<{self.name},{str(self.n)}>"


class CustomAction(Action):

    def __init__(self, name, custom_action_map):
        super().__init__(name)
        self.custom_action_map = custom_action_map

    def run(self, stack: Stack) -> Node:
        """
        实现在语义动作对象中找到语义动作并执行
        :param stack: 语法树节点栈
        :return: 语法法节点
        """
        # print(self.name, getattr(self.custom_action_map, self.name))
        return getattr(self.custom_action_map, self.name)(stack)

    def __repr__(self):
        return f"<{self.name},0>"


class LL1Grammar(Grammar):
    """
    LL1文法
    """
    def __init__(self,
                 start: str,
                 productions: List[Production],
                 terminal: set,
                 nonterminal: set,
                 action_map=None):
        super().__init__(start, productions, terminal, nonterminal)
        if action_map is None:
            action_map = {}
        for production in self.productions:
            production.seq = [x if x not in action_map else action_map[x] for x in production.seq]
        self.ll1_table: None | Dict[str, Dict[str, Production]] = None

    def first(self, sym: str | EOF | EPS | List):
        """
        对于一个符号或者一个符号序列，计算它的first集合
        :param sym: 一个符号或者一个符号序列
        :return: 该符号或序列的first集合
        """
        if isinstance(sym, list):
            ans = set()
            for s in sym:
                if isinstance(s, Action):
                    continue
                ans |= self.first(s)
                if EPS not in ans:
                    break
                ans.remove(EPS)
            else:
                ans.add(EPS)
            return ans
        if sym in self.terminal:
            return {sym}
        assert not isinstance(sym, Action)  # sym不能是Action
        assert self.first_map is not None  # First map 不能为None
        assert sym in self.first_map, sym  # 要求sym在first_map中必须初始化
        return self.first_map[sym]

    def follow(self, sym):
        """
        对于一个符号，计算follow集合
        :param sym: 一个符号
        :return: 该符号的follow集合
        """
        assert not isinstance(sym, Action)  # sym不能是Action
        assert sym in self.non_terminal     # sym必须是非终止符号
        assert self.follow_map is not None  # follow_map不能为None
        assert sym in self.follow_map, sym  # sym在follow_map中必须初始化
        return self.follow_map[sym]

    def cal_first_sets(self):
        """
        计算first集合
        :return:
        """
        if self.first_map is not None:
            return self.first_map
        self.first_map = {a: set() for a in self.non_terminal}  # 初始化first_map
        changed = True  # 变量标记变化
        while changed:
            changed = False
            for production in self.productions:
                for sym in production.seq:
                    if isinstance(sym, Action):
                        continue
                    tmp = self.first(sym)
                    changed = changed or bool(tmp - {EPS} - self.first_map[production.start])
                    # 如果first集合存在变化，设置变化标志
                    self.first_map[production.start] |= tmp - {EPS}
                    if EPS not in self.first(sym):  # 如果没有EPS，则不需要继续求解其他的first
                        break
                else:
                    self.first_map[production.start].add(EPS)
        return self.first_map

    def cal_follow_sets(self):
        """
        计算follow集合
        :return:
        """
        if self.follow_map is not None:
            return self.follow_map
        if self.first_map is None:
            self.cal_first_sets()
        self.follow_map = {a: set() for a in self.non_terminal}  # 初始化follow_map
        self.follow_map[self.start].add(EOF)  # 定义开始符的follow集合为EOF
        changed = True  # 变量标记变化
        while changed:
            changed = False
            for production in self.productions:
                for i, sym in enumerate(production.seq):
                    if sym not in self.non_terminal or isinstance(sym, Action):  # 不计算终止符号和action
                        continue
                    cache = self.first(production.seq[i + 1:])  # 将非终止符号后续的序列的first值找出并加到follow集合中
                    tmp = cache - {EPS}  # 删除EPSILON
                    changed = changed or bool(tmp - self.follow_map[sym])  # 设置变化标志
                    self.follow_map[sym] |= tmp
                    if EPS in cache:  # 如果序列中有EPSILON，则需要将产生式的左部的follow集合加入follow(sym)
                        tmp = self.follow(production.start)
                        changed = changed or bool(tmp - self.follow_map[sym])
                        self.follow_map[sym] |= tmp
        return self.follow_map

    def indirect_left_factoring(self):
        """
        去除间接左公因子
        :return:
        """

        def check_ll1_first():
            """
            first集合重复的两个产生式
            :return:
            """
            for s0 in self.non_terminal:
                mp = {}
                for px in filter(lambda x: x.start == s0, self.productions):
                    # for py in filter(lambda x: x.start == s0, self.productions):
                    #     if px == py:
                    #         continue
                    #     if self.first(px.seq) & self.first(py.seq):
                    #         return px, py
                    for sym in self.first(px.seq):
                        if sym in mp:
                            return px, mp[sym]
                        mp[sym] = px
            return None

        self.left_factoring()
        cnt = 0
        while True:
            cnt += 1
            if cnt >= 100:
                MQSever.publish(MQ_TYPE.Grammar_Error, Message("此文法不是LL(1)文法", "此文法不是LL(1)文法"))
                raise GrammarException("此文法不是LL(1)文法")
            self.clear_first_sets()
            self.clear_follow_sets()
            self.cal_first_sets()
            # 重新计算first集合
            ans = check_ll1_first()
            if ans is None:
                break
            p0, p1 = ans
            # print(p0, p1)
            if p0.left in self.non_terminal:  # 左带入(p0)
                self.productions.remove(p0)
                self.productions.extend(self.left_assign(p0))
            if p1.left in self.non_terminal:  # 左带入(p1)
                self.productions.remove(p1)
                self.productions.extend(self.left_assign(p1))
            self.left_factoring()  # 消除直接左递归
        return cnt

    def left_factoring(self):
        self.clear_first_sets()
        self.clear_follow_sets()
        """
        采用trie字典树去除左公因子
        :return:
        """
        trie = {}

        def build(seq: List):
            """
            构建字典树
            :param seq: 输入符号序列
            :return:
            """
            p = trie
            for key, raw in seq:
                if key not in p:
                    p[key] = ({}, raw)
                p = p[key][0]
            p[str(EPS)] = ({}, EPS)

        new_productions = []

        def construct(tag: str, root: dict) -> list:
            """
            从字典树中删除左公因子并构建新的产生式
            :param tag: 当前处理的标记
            :param root: 树的根节点
            :return: 新的产生式序列
            """
            nonlocal new_productions
            res = []
            for kk, (tri, raw) in root.items():
                res.append([raw] + construct(tag, tri))
            if len(res) == 0:
                return []
            elif len(res) == 1:
                return res[0]
            else:
                new_name = f"{tag}_{getRandomString(5)}"
                for x in res:
                    new_productions.append(Production(new_name, x))
                return [new_name]

        for production in self.productions:
            sq = [(production.start, production.start)] + [(str(x), x) for x in production.seq]
            # 将每个符号序列加入到树中
            build(sq)

        mp = {}
        for k, (t, r) in trie.items():
            ans = construct(r, t)
            if len(ans) == 1:
                mp[ans[0]] = r
            else:
                new_productions.append(Production(r, ans))
        for production in new_productions:
            if production.start in mp:
                production.start = mp[production.start]
            if production.seq[-1] == EPS and len(production.seq) > 1:
                del production.seq[-1]
        # 从字典树中提取左公因子并构建新的产生式
        del self.productions
        self.productions = new_productions
        self.non_terminal = set(map(lambda p: p.start, self.productions))

    def reachable_cut(self):
        self.clear_first_sets()
        self.clear_follow_sets()
        """
        BFS算法 裁剪所有不可到达的产生式
        """
        qu = [self.start]
        available = {EPS}
        while qu:  # BFS队列qu
            pos = qu.pop(0)
            if pos in available:
                continue
            available.add(pos)
            if pos in self.terminal:
                continue
            for production in filter(lambda x: x.start == pos, self.productions):
                for sym in production.seq:
                    if isinstance(sym, Action):
                        continue
                    qu.append(sym)
        cut_ter = self.terminal - available
        cut_non_ter = self.non_terminal - available
        self.terminal &= available
        self.non_terminal &= available
        cut_productions = []

        def cut(pd: Production):
            """
            闭包临时函数，实现裁剪功能
            :param pd: 产生式类型
            :return: 是否需要裁剪，True表示需要保留，False表示此产生式需要丢弃
            """
            if pd.start in cut_non_ter:
                cut_productions.append(pd)
                return False
            for sym_tmp in pd.seq:
                if isinstance(sym_tmp, Action):
                    continue
                if sym_tmp in cut_non_ter | cut_ter:
                    cut_productions.append(pd)
                    return False
            return True

        self.productions = list(filter(cut, self.productions))  # 对于每一个产生式调用cut函数
        return cut_productions, cut_non_ter, cut_ter

    def endable_cut(self):
        self.clear_first_sets()
        self.clear_follow_sets()
        """
        DFS方法去除不可终止节点
        :return:
        """

        available = set()
        path = set()

        def dfs(pos):
            """
            DFS寻找不可终止节点
            :param pos: 当前符号
            :return: 当前符号是否是可终止节点
            """
            nonlocal available, path
            if pos in path:
                return False
            if pos in self.terminal:
                return True
            if pos in available:
                return True
            path.add(pos)
            for production in filter(lambda x: x.start == pos, self.productions):
                for sym in production.seq:
                    if isinstance(sym, Action):
                        continue
                    if not dfs(sym):
                        break
                else:
                    available.add(pos)
                    path.remove(pos)
                    return True
            path.remove(pos)
            return False

        new_non_terminal = set(filter(dfs, self.non_terminal))  # 去除不可终止节点
        cut_non_ter = self.non_terminal - new_non_terminal
        cut_productions = []

        def cut(pd: Production):
            """
            闭包临时函数，实现裁剪功能
            :param pd: 产生式类型
            :return: 是否需要裁剪，True表示需要保留，False表示此产生式需要丢弃
            """
            if pd.start in cut_non_ter:
                cut_productions.append(pd)
                return False
            for sym_tmp in pd.seq:
                if isinstance(sym_tmp, Action):
                    continue
                if sym_tmp in cut_non_ter:
                    cut_productions.append(pd)
                    return False
            return True

        self.productions = list(filter(cut, self.productions))  # 对于每一个产生式调用cut函数
        self.non_terminal = new_non_terminal  # 更新非终止符号集合
        return cut_productions, cut_non_ter

    def left_assign(self, pro: Production):
        ans = []
        for tmp in list(filter(lambda p: p.start == pro.left, self.productions)):
            pos = pro.seq.index(pro.left)
            ans.append(Production(pro.start, pro.seq[:pos] + tmp.seq + pro.seq[pos + 1:]))
        return ans

    def eliminate_left_recursion(self):
        self.clear_first_sets()
        self.clear_follow_sets()
        # 将开符号放到最后处理
        symbols = list(self.non_terminal - {self.start})
        symbols.append(self.start)

        def eliminate(sym: str):
            recur = list(filter(lambda p: p.start == sym and p.left == sym, self.productions))
            if not recur:
                return
            other = list(filter(lambda p: p.start == sym and p.left != sym, self.productions))
            nn = f"{sym}_{getRandomString(5)}"  # new name
            for p in recur:
                self.productions.remove(p)
                pos = p.seq.index(p.left)
                self.productions.append(Production(nn, p.seq[:pos] + p.seq[pos + 1:] + [nn]))
            self.productions.append(Production(nn, [EPS]))
            for p in other:
                p.seq.append(nn)
            # self.non_terminal.add(nn)

        for i, si in enumerate(symbols):
            for j, sj in enumerate(symbols[:i]):
                choice: List[Production] = list(filter(lambda p: p.start == si and p.left == sj, self.productions))
                for c in choice:
                    self.productions.remove(c)
                    self.productions.extend(self.left_assign(c))
            eliminate(si)

        self.non_terminal = set(map(lambda p: p.start, self.productions))

    def fast_check_LL1(self):
        for s0 in self.non_terminal:
            mp = set()
            for p in filter(lambda x: x.start == s0, self.productions):
                st = set(self.first(p.seq))
                if st & mp:
                    return False
                mp.update(st)
            if EPS in self.first(s0):
                if self.first(s0) & self.follow(s0) != set():
                    pass
        return True

    def check_LL1(self):
        res = True
        for s0 in self.non_terminal:
            for p in filter(lambda x: x.start == s0, self.productions):
                for p1 in filter(lambda x: x.start == s0, self.productions):
                    if p == p1:
                        continue
                    if self.first(p.seq) & self.first(p1.seq):
                        print("error: ")
                        print("\t", self.first(p.seq), p)
                        print("\t", self.first(p1.seq), p1)
                        MQSever.publish(MQ_TYPE.Grammar_Error, Message(f"first集合冲突",
                                                                       f"{str(p)}\n"
                                                                       f"{str(p1)}"))
                        return False
            if EPS in self.first(s0):
                if self.first(s0) & self.follow(s0) != set():
                    print("warning: ", s0)
                    print("\tfirst: ", self.first(s0))
                    print("\tfollow: ", self.follow(s0))
                    MQSever.publish(MQ_TYPE.Grammar_Warning, Message(f"文法: {s0} 中，first与follow集合冲突",
                                                                     f"first: {str(self.first(s0))}\n"
                                                                     f"follow: {str(self.follow(s0))}"))
        return res

    def to_LL1_table(self):
        assert self.fast_check_LL1(), "不是LL1文法"
        self.ll1_table = {s: {} for s in self.non_terminal}
        for p in self.productions:
            for sym in self.first(p.seq):
                if sym == EPS:
                    continue
                if sym in self.ll1_table[p.start] and self.ll1_table[p.start].get(sym, None) != p:
                    # print("Warning:")
                    # print("\t", self.ll1_table[p.start][sym])
                    # print("\t", p)
                    MQSever.publish(MQ_TYPE.Grammar_Warning, Message(f"LL(1)分析表构建时，存在使用最长匹配原则",
                                                                     f"采用 {str(max(self.ll1_table[p.start][sym], p, key=lambda px: len(px.seq)))}\n"
                                                                     f"未采用 {str(min(self.ll1_table[p.start][sym], p, key=lambda px: len(px.seq)))}"))
                    self.ll1_table[p.start][sym] = max(self.ll1_table[p.start][sym], p, key=lambda px: len(px.seq))
                else:
                    self.ll1_table[p.start][sym] = p
            if EPS in self.first(p.seq):
                for sym in self.follow(p.start):
                    if sym in self.ll1_table[p.start] and self.ll1_table[p.start].get(sym, None) != p:
                        # print("Warning:")
                        # print("\t", self.ll1_table[p.start][sym])
                        # print("\t", p)
                        self.ll1_table[p.start][sym] = max(self.ll1_table[p.start][sym], p, key=lambda px: len(px.seq))
                    else:
                        self.ll1_table[p.start][sym] = p
        return self.ll1_table

    def analysis(self, tokens: List[Tuple[str, str]]) -> Node | None:
        """
        根据token序列分析生成语法树
        :param tokens: 输入token序列，格式为 [(tokenType, raw),...]
        :return: 生成的语法树
        """
        assert self.ll1_table is not None
        tokens.append((EOF, ""))
        parsing_stack = Stack()
        parsing_stack.push(EOF, self.start)
        value_stack = Stack()
        while parsing_stack.top() != EOF:
            if isinstance(parsing_stack.top(), Action):
                action = parsing_stack.pop()
                value_stack.push(action.run(value_stack))
            elif parsing_stack.top() in self.terminal and parsing_stack.top() == tokens[0][0]:
                parsing_stack.pop()
                value_stack.push(tokens.pop(0))
            elif parsing_stack.top() in self.non_terminal and self.ll1_table[parsing_stack.top()][tokens[0][0]]:
                p = self.ll1_table[parsing_stack.top()][tokens[0][0]]
                parsing_stack.pop()
                parsing_stack.push(*filter(lambda x: x != EPS, p.seq[::-1]))
            else:
                print("Error.")
                break
        if tokens[0][0] == EOF and parsing_stack.top() == EOF:
            return value_stack.pop()
        else:
            return None

    def add_LL1_action(self):
        for p in self.productions:
            # if all(map(lambda x: x in self.terminal, p.seq)):
            #     continue
            p.seq.append(LL1InterAction(f"{str(p)}", len(p.seq)))


class FileGrammarParse(GrammarParse):

    def __init__(self, path, custom_action_map=None):
        self.path: str = path
        self.cam = custom_action_map

    def compile(self) -> LL1Grammar:

        def translate(s: str):
            if s.startswith("<") and s.endswith(">"):
                s = s[1:-1]
                if s.upper() == "EPS":
                    return EPS
                else:
                    pos = s.find(",")
                    name, n = s[:pos], int(s[pos + 1:])
                    return LL1InterAction(name, n) if n != 0 else CustomAction(name, self.cam)
            else:
                return s

        import re
        if not os.path.exists(self.path):
            MQSever.publish(MQ_TYPE.Grammar_Error, Message(f"不存在文件 {self.path}"))
            raise FileGrammarParseException(f"不存在此文件 {self.path}")
        with open(self.path, "r") as f:
            data = f.read()

        sentences = [x.strip() for x in data.split(";") if x.strip()]
        sentences = list(filter(lambda x: x,
                                map(lambda x: x[:x.rfind('//')].strip() if x.rfind('//') != -1 else x, sentences)))
        productions = []
        non_terminal = set()
        terminal = set()
        start = None
        # print(sentences)
        for sentence in sentences:
            if "::=" in sentence:
                r = re.match(r"(?P<prefix>[a-zA-Z0-9\-_]+?)\s*::=\s*(?P<content>(.|\n)+)", sentence)
                assert r is not None
                prefix = r.groupdict().get('prefix', None).strip()
                content = r.groupdict().get('content', None).strip()
                for pattern in content.split("|"):
                    pattern = list(map(translate, pattern.strip().split()))
                    productions.append(Production(prefix, pattern))
            elif sentence.startswith("G"):
                r = re.match(r"G\[\s*(\S+)\s*]", sentence)
                assert r is not None
                start = r.group(1).strip()
            else:
                r = re.match(r"(?P<prefix>[a-z\-]+?)\s*\{(?P<content>(.|\n)+?)}", sentence)
                assert r is not None
                prefix = r.groupdict().get('prefix', None).strip()
                content = r.groupdict().get('content', None).strip()
                # print(prefix, content)
                if prefix == "non-terminal":
                    non_terminal.update(set(map(lambda x: x.strip(), content.strip().split())))
                elif prefix == 'terminal':
                    terminal.update(set(map(lambda x: translate(x.strip()), content.strip().split())))
                else:
                    MQSever.publish(MQ_TYPE.Grammar_Error, Message(f"未知词语 {prefix}"))
                    raise FileGrammarParseException(f"未知关键字 {prefix}")
        non_terminal |= set(map(lambda p: p.start, productions))
        if not start:
            MQSever.publish(MQ_TYPE.Grammar_Error, Message(f"缺少定义语句 `G[文法开符号]`"))
            raise FileGrammarParseException(f"缺少定义语句 `G[文法开符号]`")
        if not non_terminal:
            MQSever.publish(MQ_TYPE.Grammar_Error, Message("缺少定义语句 `non-terminal {非终止符号(空格或回车隔开)}`"))
            raise FileGrammarParseException("缺少定义语句 `non-terminal {非终止符号(空格或回车隔开)}`")
        if not terminal:
            MQSever.publish(MQ_TYPE.Grammar_Error, Message("缺少定义语句 `terminal {终止符号(空格或回车隔开)}`"))
            raise FileGrammarParseException("缺少定义语句 `terminal {终止符号(空格或回车隔开)}`")
        return LL1Grammar(start, productions, terminal, non_terminal)

    @staticmethod
    def to_str(g: LL1Grammar) -> str:

        def translate(x):
            if isinstance(x, LL1InterAction):
                return f"<{x.name},{x.n}>"
            if isinstance(x, CustomAction):
                return f"<{x.name},0>"
            if isinstance(x, _EPSILON):
                return f"<EPS>"
            return x

        s = f"G[{g.start}];\n\n"
        for p in g.productions:
            p: Production
            s += f"{p.start} ::= " + " ".join(map(translate, p.seq)) + ";\n"
        s += "\n"

        s += "non-terminal {\n" + "\n".join(g.non_terminal) + "\n};\n\n"
        s += "terminal {\n" + "\n".join(map(translate, g.terminal)) + "\n};\n\n"

        return s

    @staticmethod
    def save(g, path):
        with open(path, "w") as f:
            f.write(FileGrammarParse.to_str(g))


class GrammarExecute:

    def __init__(self, g: LL1Grammar):
        self.g = g
        self.g.cal_first_sets()
        self.g.cal_follow_sets()
        assert self.g.fast_check_LL1()
        self.g.to_LL1_table()

    def analysis_lex_file(self, path):
        with open(path, "r") as f:
            data = f.readlines()

        def cut(s: str):
            pos = s.find(" ")
            return s[:pos], s[pos + 1:]

        sentences = list(map(lambda x: (x[0].strip(), eval(x[1].strip())),
                             map(cut, filter(lambda x: x.strip(), data))))
        return self.g.analysis(sentences)

    def ll1_table(self):
        def translate(x):
            if isinstance(x, LL1InterAction):
                return f"<{x.name},{x.n}>"
            if isinstance(x, CustomAction):
                return f"<{x.name},0>"
            if isinstance(x, _EPSILON):
                return f"<EPS>"
            return x

        ans = {}
        for s0, mp in self.g.to_LL1_table().items():
            tmp = {}
            for s1, p in mp.items():
                if isinstance(s1, _EOF):
                    s1 = "$"
                tmp[s1] = f"{p.start} ::= " + " ".join(map(translate, p.seq)) + ";"
            ans[s0] = tmp
        return ans


class CustomActionCodeParse:
    """
    将用户输入的语义动作python文件执行，并得到对象
    customActionMap = CustomActionCodeParse(filename).getMap()
    """
    def __init__(self, code):
        self.code: str = code
        # self.code = self.code.replace("from", "# from").replace("import", "# import")
        self.code = re.sub(r"from[ \S]+import[ \S]+", "", self.code)
        self.code = re.sub(r"import[ \S]+", "", self.code)
        # self.code = "\n".join(
        #     map(lambda x: "    " + x, self.code.split('\n'))
        # )
        # self.code = "class context:\n" + self.code

    def getMap(self):
        ls = {}
        exec(self.code, {"Node": Node, "Stack": Stack, "Context": Context, "types": types}, ls)
        return ls['define']
