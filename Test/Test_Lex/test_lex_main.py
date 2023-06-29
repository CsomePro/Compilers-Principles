import unittest

from Lexical.Lex import Lex
from kit.MQKit import MQ_TYPE, MQueueClient

lex_graph = MQueueClient("lex_graph")
lex_graph.subscribe(MQ_TYPE.Lex_Graph_Pipe)

class Test_lex(unittest.TestCase):

    def test_lex(self):
        lex = Lex(Lex.read_file('tiny.l'))
        # print(lex.expr_list)
        g = lex.graph
        print(g.to_json())
        print("log g\n ",g)
        # code, array = lex.generate_lex()
        lex_code = lex.getLex()
        # print(lex_code)
        lex.saveLex("tiny.lex.c")
        print(len(lex.graph.nodes), len(lex.graph.edges))

        for msg in lex_graph:
            print(msg)
