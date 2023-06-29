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

import argparse
import dis
import functools
import json
import marshal
import os
from io import StringIO

from Grammar.Context import Context
from Grammar.Grammar import FileGrammarParse, GrammarExecute, CustomActionCodeParse
from Lexical.Lex import Lex
from kit.MQKit import MQ_TYPE, MQueueClient, Message

lex_graph_pipe = MQueueClient("lex_graph")
lex_graph_pipe.subscribe(MQ_TYPE.Lex_Graph_Pipe)


class args:

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser

    def __call__(self, func):
        for arg_name, arg_type in func.__annotations__.items():
            self.parser.add_argument(f"-{arg_name}", required=True, type=arg_type)

        @functools.wraps(func)
        def tmp(_args: argparse.Namespace):
            func(**{k: getattr(_args, k) for k in func.__annotations__.keys()})

        self.parser.set_defaults(func=tmp)
        return func


main_parser = argparse.ArgumentParser(prog='PROG')
subparsers = main_parser.add_subparsers(help='sub-command help')


@args(main_parser)
def default():
    main_parser.print_help()


lex_parsers = subparsers.add_parser("lex", help='Lex')
lex_sub_parsers = lex_parsers.add_subparsers(help="lex sub command")


@args(lex_parsers)
def lex_default():
    lex_parsers.print_help()


@args(lex_sub_parsers.add_parser('compile', help="编译正则表达式文件到C语言文件"))
def lex_compile(f: str, o: str):
    assert os.path.exists(f), f"{f} 文件不存在"
    lex = Lex(Lex.read_file(f))
    lex.saveLex(o)
    code = lex.getLex()
    NFA = {}
    DFA = {}
    SDFA = {}
    final_SDFA = ""
    for gs in lex_graph_pipe:
        gs: Message
        if "::" in gs.brief:
            t, raw = gs.brief.split("::")
            {"NFA": NFA, "DFA": DFA, "SDFA": SDFA}[t][raw] = json.loads(gs.detail)
        else:
            assert gs.brief == "SDFA"
            final_SDFA = json.loads(gs.detail)
    lex_graph_pipe.clear()
    print(json.dumps(dict(
        code=code,
        NFA=NFA,
        DFA=DFA,
        SDFA=SDFA,
        final=final_SDFA
    )), end="")


grammar_parsers = subparsers.add_parser("grammar", help='Grammar')
grammar_sub_parsers = grammar_parsers.add_subparsers(help="Grammar Menu")

@args(grammar_parsers)
def grammar_default():
    grammar_parsers.print_help()

@args(grammar_sub_parsers.add_parser('simplify', help="化简文法"))
def grammar_simplify(f: str, o: str):
    assert os.path.exists(f), f"{f} 文件不存在"
    g = FileGrammarParse(f).compile()
    g.reachable_cut()
    g.endable_cut()
    part1 = FileGrammarParse.to_str(g)
    g.left_factoring()
    g.eliminate_left_recursion()
    g.indirect_left_factoring()
    g.reachable_cut()
    g.endable_cut()
    part2 = FileGrammarParse.to_str(g)
    first = {
        k: list(map(str, v)) for k, v in g.cal_first_sets().items()
    }
    follow = {
        k: list(map(str, v)) for k, v in g.cal_follow_sets().items()
    }
    FileGrammarParse.save(g, o)
    ll1_table = GrammarExecute(g).ll1_table()
    print(json.dumps(dict(
        part1=part1,
        part2=part2,
        first=first,
        follow=follow,
        ll1_table=ll1_table
    )), end="")


@args(grammar_sub_parsers.add_parser('syntax', help="化简后文法并匹配"))
def grammar_compile(f: str, e: str, lex: str):
    assert os.path.exists(f), f"{f} 文件不存在"
    assert os.path.exists(lex), f"{lex} 文件不存在"
    if e:
        assert os.path.exists(e), f"{e} 文件不存在"
        with open(e, "r", encoding="utf-8") as file:
            code = file.read()
        custom_action = CustomActionCodeParse(code).getMap()
        g = FileGrammarParse(f, custom_action()).compile()
    else:
        g = FileGrammarParse(f).compile()
    g.cal_first_sets()
    g.cal_follow_sets()
    node = GrammarExecute(g).analysis_lex_file(lex)
    print(json.dumps(node.to_json()), end="")


@args(grammar_sub_parsers.add_parser('all', help="合并所有功能"))
def grammar_compile(f: str, e: str, lex: str):
    assert os.path.exists(f), f"{f} 文件不存在"
    assert os.path.exists(lex), f"{lex} 文件不存在"
    assert os.path.exists(e), f"{e} 文件不存在"
    with open(e, "r", encoding="utf-8") as file:
        code = file.read()
    custom_action = CustomActionCodeParse(code).getMap()
    g = FileGrammarParse(f, custom_action()).compile()
    g.cal_first_sets()
    g.cal_follow_sets()
    node = GrammarExecute(g).analysis_lex_file(lex)
    gs = Context()
    code_obj = node.compile(gs, None)
    with StringIO() as f:
        dis.dis(code_obj, file=f)
        size = f.tell()
        f.seek(0)
        code = f.read(size)
        print(json.dumps(dict(
            code=code,
            globals="",
            bytecode=marshal.dumps(code_obj).hex()
        )), end="")


exec_parsers = subparsers.add_parser("exec", help='Grammar')

@args(exec_parsers)
def exec_code():
    # gs = json.loads(input())
    # code = input()
    # print(f"[+] ByteCode: {code}")
    # co_consts = gs['const']
    # co_globals = gs['extra']['co_globals']
    # co_sym = ["" for _ in gs["sym_table"]]
    # code = bytes.fromhex(code)
    # for k, v in gs["sym_table"].items():
    #     idx, _ = v
    #     co_sym[idx] = k
    # code_exec = CodeType(0, 0, 0, len(co_sym), 0, 0, bytes(code), tuple(co_consts), tuple(co_globals), tuple(co_sym),
    #                      "", "", 0, b'')
    code_hex = input()
    code_obj = bytes.fromhex(code_hex)
    print(f"[+] Code Object: {code_hex}")
    code_exec = marshal.loads(code_obj)
    print(f"[+] Running...")
    result = eval(code_exec, {}, {})
    print(f"[+] Stopped. Result: {result}")


parse_args = main_parser.parse_args()
parse_args.func(parse_args)
