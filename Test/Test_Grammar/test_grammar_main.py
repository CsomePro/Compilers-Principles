import dis
import json
import unittest
from Grammar.Grammar import LL1Grammar, Production, FileGrammarParse, GrammarExecute, CustomActionCodeParse
from Grammar.Base import EPS, EOF, Action, InterNode
from Grammar.Context import Context

# def print_tree(pos: Node, indent=0):
#     print("\t" * indent, f"{pos.name}{{", sep="")
#     for n in pos.child:
#         if isinstance(n, Node):
#             print_tree(n, indent + 1)
#         else:
#             print("\t" * (indent + 1), f"{n},", sep="")
#     print("\t" * indent, "},", sep="")


class Test_ll1_grammar(unittest.TestCase):

    def test_first_follow(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop term'.split(' ')),
                Production('exp', 'term'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('term', 'term mulop factor'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '*'.split(' ')),
                Production('factor', '( exp )'.split(' ')),
                Production('factor', 'number'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
        )
        print(g)
        ans_first = {
            'exp': {'(', 'number'},
            'term': {'(', 'number'},
            'factor': {'(', 'number'},
            'addop': {'+', '-'},
            'mulop': {'*'},
        }
        ans_follow = {
            'exp': {EOF, *("+ - )".split())},
            'addop': {*("( number".split())},
            'term': {EOF, *("+ - * )".split())},
            'mulop': {*("( number".split())},
            'factor': {EOF, *("+ - * )".split())},
        }
        print("ans_first:", ans_first)
        print("ans_follow:", ans_follow)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        # print({1, 2, *"1 2".split()})
        for name, st in g.cal_first_sets().items():
            self.assertSetEqual(ans_first[name], st, f"{name}, {ans_first[name]}, {st}")
        for name, st in g.cal_follow_sets().items():
            self.assertSetEqual(ans_follow[name], st, f"{name}, {ans_follow[name]}, {st}")

    def test_some_action(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop 11 term'.split(' ')),
                Production('exp', '11 term'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('term', 'term 11 mulop factor'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '* 11'.split(' ')),
                Production('factor', '( 11 exp )'.split(' ')),
                Production('factor', '11 number 11'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
            {"11": Action("11")}
        )
        print(g)
        ans_first = {
            'exp': {'(', 'number'},
            'term': {'(', 'number'},
            'factor': {'(', 'number'},
            'addop': {'+', '-'},
            'mulop': {'*'},
        }
        ans_follow = {
            'exp': {EOF, *("+ - )".split())},
            'addop': {*("( number".split())},
            'term': {EOF, *("+ - * )".split())},
            'mulop': {*("( number".split())},
            'factor': {EOF, *("+ - * )".split())},
        }
        print(ans_first)
        print(ans_follow)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        # print({1, 2, *"1 2".split()})
        for name, st in g.cal_first_sets().items():
            self.assertSetEqual(ans_first[name], st, f"{name}, {ans_first[name]}, {st}")
        for name, st in g.cal_follow_sets().items():
            self.assertSetEqual(ans_follow[name], st, f"{name}, {ans_follow[name]}, {st}")

    def test_left_factoring(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop term 11'.split(' ')),
                Production('exp', 'term 11'.split(' ')),
                Production('exp', 'term number 11'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('addop', []),
                Production('term', 'term mulop factor 11'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '* 11'.split(' ')),
                Production('factor', '( exp ) 11'.split(' ')),
                Production('factor', 'number 11'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
            {"11": Action("11")}
        )
        g.left_factoring()
        print(g)
        # a = Action('122')
        # b = Action('122')
        # c = Action('321')
        # d = a
        # print(a == b, a is b)
        # print(a == c, a is c)
        # print(a == d, a is d)
        # print({a, b, c, d})
        # print(isinstance(a, Action), isinstance(b, Action))

    def test_reachable_cut(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop term 11'.split(' ')),
                Production('exp', 'term 11'.split(' ')),
                Production('exp', 'term number 11'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('addop', []),
                Production('term', 'term factor 11'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '* 11'.split(' ')),
                Production('factor', '( exp ) 11'.split(' ')),
                Production('factor', 'number 11'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
            {"11": Action("11")}
        )
        print(g.reachable_cut())
        print(g)

    def test_endable_cut(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop term 11'.split(' ')),
                Production('exp', 'term 11'.split(' ')),
                Production('exp', 'term number 11'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('addop', []),
                Production('term', 'term mulop factor 11'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '* mulop'.split(' ')),
                Production('factor', '( exp ) 11'.split(' ')),
                Production('factor', 'number 11'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
            {"11": Action("11")}
        )
        print(g.endable_cut())
        print(g)

    def test_eliminate_left_recursion(self):
        g = LL1Grammar(
            "B",
            [
                Production('A', 'B a 11'.split()),
                Production('A', 'A a 11'.split()),
                Production('A', 'c 11'.split()),
                Production('B', 'B b 11'.split()),
                Production('B', 'A b 11'.split()),
                Production('B', 'd 11'.split()),
            ],
            set('a b c d'.split()),
            set('A B'.split()),
            {"11": Action("11")}
        )
        print(g)
        # g.reachable_cut()
        # print(g)
        # g.endable_cut()
        # print(g)
        # print([1,2,1].index(1))
        g.eliminate_left_recursion()
        g.cal_first_sets()
        g.cal_follow_sets()
        print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        # print(g.LL1check())

    def test_ll1_main(self):
        g = LL1Grammar(
            "exp",
            [
                Production('exp', 'exp addop term'.split(' ')),
                Production('exp', 'term'.split(' ')),
                Production('addop', '+'.split(' ')),
                Production('addop', '-'.split(' ')),
                Production('term', 'term mulop factor'.split(' ')),
                Production('term', 'factor'.split(' ')),
                Production('mulop', '*'.split(' ')),
                Production('factor', '( exp )'.split(' ')),
                Production('factor', 'number'.split(' ')),
            ],
            set('+ - * ( ) number'.split()),
            set('exp addop term mulop factor'.split()),
        )
        print(g)
        # g.reachable_cut()
        # g.endable_cut()
        # g.left_factoring()
        print(g.add_LL1_action())
        g.eliminate_left_recursion()
        print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        print(g.fast_check_LL1())
        for s0, mp in g.to_LL1_table().items():
            print(s0)
            for s1, p in mp.items():
                print("\t", repr(s1), "-->", p)
        tks = [
            ("number", '1'),
            ("+", '+'),
            ("number", '2'),
            ("*", '*'),
            ("number", '3'),
            ("+", '+'),
            ("number", '2'),
            ("*", '*'),
            ("number", '3'),
        ]
        node = g.analysis(tks)
        print(node)
        node.simplify()
        print(node)

        print_tree(node)


from kit.MQKit import MQueueClient, MQSever, MQ_TYPE

grammar_mq_client = MQueueClient("grammar_mq")
grammar_mq_client.subscribe(MQ_TYPE.Grammar_Error)
grammar_mq_client.subscribe(MQ_TYPE.Grammar_Warning)

def p_code(code):
    for x in code.__dir__():
        x: str
        if x.startswith("co_"):
            print(x, "=", getattr(code, x))

class Test_file_parse(unittest.TestCase):

    def test_compile(self):
        g = FileGrammarParse('./tiny2.g').compile()
        print(g)
        print(g.reachable_cut())
        print(g.endable_cut())
        print(g)
        # print(g.add_LL1_action())
        g.left_factoring()
        print(g)
        g.eliminate_left_recursion()
        print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        print(g.fast_check_LL1())
        for s0, mp in g.to_LL1_table().items():
            print(s0)
            for s1, p in mp.items():
                print("\t", repr(s1), "-->", p)
        ge = GrammarExecute(g)
        node = ge.analysis_lex_file("./tiny.lex")
        node = node.simplify()
        # node.simplify()
        print_tree(node)

    def test_2(self):
        # def print(*args):
        #     pass
        g = FileGrammarParse('./minic4.g').compile()
        # print(g)
        print(g.reachable_cut())
        print(g.endable_cut())
        # print(g.add_LL1_action())
        g.left_factoring()
        g.eliminate_left_recursion()
        g.left_factoring()
        print("cnt: ", g.indirect_left_factoring())
        # print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        print(g.non_terminal)
        print(g.terminal)
        print(g)

        if not g.fast_check_LL1():
            print(g.check_LL1())
        # g.to_LL1_table()
        print("LL1 Table::")
        for s0, mp in g.to_LL1_table().items():
            print(s0)
            for s1, p in mp.items():
                print("\t", repr(s1), "-->", p)
        ge = GrammarExecute(g)
        node = ge.analysis_lex_file("./minic.lex")
        node = node.simplify()
        # node.simplify()
        print_tree(node)
        print(grammar_mq_client)
        # grammar_mq_client.clear()
        # print(grammar_mq_client)

    def test_some_action(self):
        g = LL1Grammar(
            "A",
            [
                Production('A', 'B C c'.split(' ')),
                Production('A', 'g D B'.split(' ')),
                Production('B', 'b C D E'.split(' ')),
                Production('B', [EPS]),
                Production('C', 'D a B'.split(' ')),
                Production('C', 'c a'.split(' ')),
                Production('D', 'd D'.split(' ')),
                Production('D', [EPS]),
                Production('E', 'g A f'.split(' ')),
                Production('E', 'c'.split(' ')),
            ],
            set('a b c d e f g'.split()),
            set('A B C D E'.split()),
        )
        print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())

    def test_3(self):
        def print(*args):
            pass
        with open("extend_tiny.py", "r") as f:
            code = f.read()
        custom_action = CustomActionCodeParse(code).getMap()
        g = FileGrammarParse('./tiny_custom.g', custom_action()).compile()
        # print(g)
        print(g.reachable_cut())
        print(g.endable_cut())
        # print(g.add_LL1_action())
        g.left_factoring()
        g.eliminate_left_recursion()
        print("cnt: ", g.indirect_left_factoring())
        # print(g)
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        print(g.non_terminal)
        print(g.terminal)
        print(g)

        if not g.fast_check_LL1():
            print(g.check_LL1())
        # g.to_LL1_table()
        # print("LL1 Table::")
        # for s0, mp in g.to_LL1_table().items():
        #     print(s0)
        #     for s1, p in mp.items():
        #         print("\t", repr(s1), "-->", p)
        ge = GrammarExecute(g)
        node = ge.analysis_lex_file("./tiny.lex")
        # node = node.simplify()
        # node.simplify()
        print(node)
        print(json.dumps(node.to_json(), indent=2))
        print(grammar_mq_client)
        gs = Context()
        code = node.compile(gs, Context())
        print(code)
        print("\n".join(map(lambda x: f"{x[0]}\t\t{x[1]}", zip(range(0, len(code)*2, 2), code))))
        print(gs.to_json())
        # grammar_mq_client.clear()
        # print(grammar_mq_client)

    def test_4(self):
        # def print(*args):
        #     pass
        with open("../../minic_test/extand_minic.py", "r", encoding="utf-8") as f:
            code = f.read()
        custom_action = CustomActionCodeParse(code).getMap()
        g = FileGrammarParse('../../minic_test/minic_custom.g', custom_action()).compile()
        # print(g)
        print(g.reachable_cut())
        print(g.endable_cut())
        # print(g.add_LL1_action())
        g.left_factoring()
        g.eliminate_left_recursion()
        print("cnt: ", g.indirect_left_factoring())
        # print(g)
        print(g.reachable_cut())
        print(g.endable_cut())
        print(g.cal_first_sets())
        print(g.cal_follow_sets())
        print(g.non_terminal)
        print(g.terminal)
        print(g)

        if not g.fast_check_LL1():
            print(g.check_LL1())
        # g.to_LL1_table()
        # print("LL1 Table::")
        # for s0, mp in g.to_LL1_table().items():
        #     print(s0)
        #     for s1, p in mp.items():
        #         print("\t", repr(s1), "-->", p)
        ge = GrammarExecute(g)
        node = ge.analysis_lex_file("../../minic_test/minic.lex")
        # node = node.simplify()
        # node.simplify()
        print(node)
        print(json.dumps(node.to_json(), indent=2))
        print(grammar_mq_client)
        gs = Context()
        code = node.compile(gs, None)
        # print(code)
        #
        # print()
        # p_code(code)
        # print()
        # p_code(code.co_consts[0])
        # print()
        # p_code(code.co_consts[0].co_consts[1])
        # print()
        # p_code(code.co_consts[0].co_consts[3])

        dis.dis(code)
        print(f"[+] Running...")
        # import pdb
        # pdb.set_trace()
        ret = eval(code, {}, {})
        print(f"[+] Stopped. Code: {ret}")
        # print("\n".join(map(lambda x: f"{x[0]}\t\t{x[1]}", zip(range(0, len(code)*2, 2), code))))
        # print(gs.to_json())

    def test_5(self):

        # with open("extend_tiny.py", "r") as f:
        #     code = f.read()
        # custom_action = CustomActionCodeParse(code).getMap()
        g = FileGrammarParse('./rules(eliminate_for_csm).txt').compile()
        # print(g)
        # print(g.reachable_cut())
        # print(g.endable_cut())
        # # print(g.add_LL1_action())
        # g.left_factoring()
        # g.eliminate_left_recursion()
        # print("cnt: ", g.indirect_left_factoring())
        # print(g)
        print("first: ")
        for k, v in g.cal_first_sets().items():
            print("\t",k, v)
        print("follow: ")
        for k, v in g.cal_follow_sets().items():
            print("\t",k, v)
        # print(g.non_terminal)
        # print(g.terminal)
        # print(g)
        #
        # if not g.fast_check_LL1():
        #     print(g.check_LL1())
        # # g.to_LL1_table()
        # # print("LL1 Table::")
        # # for s0, mp in g.to_LL1_table().items():
        # #     print(s0)
        # #     for s1, p in mp.items():
        # #         print("\t", repr(s1), "-->", p)
        # ge = GrammarExecute(g)
        # node = ge.analysis_lex_file("./tiny.lex")
        # # node = node.simplify()
        # # node.simplify()
        # print(node)
        # print(json.dumps(node.to_json(), indent=2))
        # print(grammar_mq_client)
        # gs = Context()
        # code = node.compile(gs, Context())
        # print(code)
        # print("\n".join(map(lambda x: f"{x[0]}\t\t{x[1]}", zip(range(0, len(code)*2, 2), code))))
        # print(gs.to_json())
        # # grammar_mq_client.clear()
        # # print(grammar_mq_client)