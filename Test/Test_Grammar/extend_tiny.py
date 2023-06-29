from Grammar.Base import Node, Stack
from Grammar.Context import Context


# [(0, '<'), (1, '<='), (2, '=='), (3, '!='), (4, '>'), (5, '>='), (6, 'in'), (7, 'not in'), (8, 'is'), (9, 'is not'), (10, 'exception match'), (11, 'BAD')]

class define:
    class SelfNode(Node):

        def __init__(self, name, child: [Node] = None):
            super().__init__()
            self.name = name
            if child is None:
                child = []
            self.child: [Node] = child

        def to_json(self):
            return {
                "name": self.name,
                "children": [n.to_json() for n in self.child]
            }

        def __repr__(self):
            return f"{self.name}({repr(len(self.child))})"

        def simplify(self):
            pass

    class NoCompileNode(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("NoCompileNode", self)
            assert 1 != 1, "No Compile!"

    class read_node(SelfNode):
        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("read_node", self)
            argn = self.name[5:-1]
            if global_c.getVar(argn) is None:
                idx = global_c.getVarSize()
                global_c.setVar(argn, (idx, "int"))
            return [f"READ {argn} # call input"]

    class write_node(SelfNode):
        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("write_node", self)
            code = self.child[0].compile(global_c, None)
            return code + ["PRINT_EXPR"]

    class exp_node(SelfNode):
        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("exp_node", self)
            return {
                "+": lambda lc, rc: lc + rc + ["BINARY_ADD"],
                "-": lambda lc, rc: lc + rc + ["BINARY_SUBTRACT"],
                "*": lambda lc, rc: lc + rc + ["BINARY_MULTIPLY"],
                "/": lambda lc, rc: lc + rc + ["BINARY_FLOOR_DIVIDE"],
                "=": lambda lc, rc: lc + rc + ["COMPARE_OP 2 # (==)"],
                "<": lambda lc, rc: lc + rc + ["COMPARE_OP 0 # (<)"],
            }[self.name](
                self.child[0].compile(global_c, None),
                self.child[1].compile(global_c, None)
            )

    class factor_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("factor_node", self)
            tmp = self.name.find("(")
            token, raw = self.name[:tmp], self.name[tmp + 1:-1]
            if token == "ID":
                idx, t = global_c.getVar(raw)
                return [f"LOAD_FAST {idx} # ({raw})"]
            elif token == "NUMBER":
                idx = global_c.setConst(int(raw))
                return [f"LOAD_CONST {idx} # ({raw})"]
            else:
                assert 1 != 1, "Unknown"

    class stmt_seq_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("stmt_seq_node", self)
            ans = []
            for n in self.child:
                ans.extend(n.compile(global_c, None))
            return ans

    class assign_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("assign_node", self)
            sym, exp = self.child
            exp_code = exp.compile(global_c, None)
            temp = global_c.getVar(sym.name)
            if temp is None:
                idx = global_c.getVarSize()
                global_c.setVar(sym.name, (idx, "int"))
            idx, t = global_c.getVar(sym.name)
            return exp_code + [f"STORE_FAST {idx} # {sym.name}"]

    class repeat_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("repeat_node", self)
            seq, exp = self.child
            seq: Node
            exp: Node
            seq_code = seq.compile(global_c, None)
            exp_code = exp.compile(global_c, None)
            entry_label = "repeat_" + Context.getRandomStr(4)
            return [
                f"label %{entry_label}%",
                *seq_code,
                *exp_code,
                f"POP_JUMP_IF_FALSE %{entry_label}%"
            ]

    class if_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("if_node", self)
            if len(self.child) == 2:
                exp, seq = self.child
                exp: Node
                seq: Node
                exp_code = exp.compile(global_c, None)
                seq_code = seq.compile(global_c, None)
                end_label = "if_end_" + Context.getRandomStr(4)
                return [
                    *exp_code,
                    f"POP_JUMP_IF_FALSE %{end_label}%",
                    *seq_code,
                    f"label %{end_label}%",
                ]
            else:
                exp, seq0, seq1 = self.child
                exp: Node
                seq0: Node
                seq1: Node
                exp_code = exp.compile(global_c, None)
                seq0_code = seq0.compile(global_c, None)
                seq1_code = seq1.compile(global_c, None)
                false_label = "if_false_" + Context.getRandomStr(4)
                end_label = "if_end_" + Context.getRandomStr(4)
                return [
                    *exp_code,
                    f"POP_JUMP_IF_FALSE %{end_label}%",
                    *seq0_code,
                    f"JUMP_ABSOLUTE %{end_label}%",
                    f"label %{false_label}%",
                    *seq1_code,
                    f"label %{end_label}%",
                ]

    class program_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            seq: Node = self.child[0]
            code: [str] = seq.compile(global_c, local_c)
            release_code = []
            label_map = {}
            for s in code:
                s: str
                if s.startswith("label"):
                    label = s[s.find("%") + 1:s.rfind("%")]
                    label_map[label] = len(release_code)
                    continue
                if s.startswith("READ"):
                    s = s.replace("READ", "")
                    s = s[:s.find("#")].strip()
                    idx, t = global_c.getVar(s)
                    release_code.extend([
                        "LOAD_GLOBAL 1 # (int)",
                        "LOAD_GLOBAL 0 # (input)",
                        "CALL_FUNCTION 0",
                        "CALL_FUNCTION 1",
                        f"STORE_FAST {idx} # ({s})"])
                    continue
                release_code.append(s)

            def exchange(x: str):
                if "%" in x:
                    tmp = x[x.find("%") + 1:x.rfind("%")]
                    y = str(label_map[tmp] * 2)
                    return x[:x.find("%")] + y + x[x.rfind("%") + 1:]
                return x
            release_code.extend(["LOAD_CONST 0 # (None)", "RETURN_VALUE"])
            global_c.setExtra("co_globals", ("input", "int"))
            return list(map(exchange, release_code))

    def prog(self, stack: Stack) -> Node:
        return self.program_node("program", [stack.pop()])

    def read(self, stack: Stack) -> Node:
        # print("read", stack)
        token, raw = stack.pop()
        stack.pop()
        return self.read_node(f"read({raw})")

    def write(self, stack: Stack) -> Node:
        # print("write", stack)
        e = stack.pop()
        stack.pop()
        return self.write_node(f"write", [e])

    def exp(self, stack: Stack) -> Node:
        # print("exp", stack)
        rc = stack.pop()
        token, op = stack.pop()
        lc = stack.pop()
        return self.exp_node(f"{op}", [lc, rc])

    def factor_lp_rp(self, stack: Stack) -> Node:
        # print("factor_lp_rp", stack)
        stack.pop()
        node = stack.pop()
        stack.pop()
        return node

    def factor(self, stack: Stack) -> Node:
        # print("factor", stack)
        token, raw = stack.pop()
        return self.factor_node(f"{token}({raw})")

    def stmt(self, stack: Stack) -> Node:
        # print("stmt", stack)
        statement = stack.pop()
        stack.pop()
        node = stack.pop()
        if node.name != 'stmt':
            return self.stmt_seq_node(f"stmt-seq", [node, statement])
        node.child.append(statement)
        return node

    def assign(self, stack: Stack) -> Node:
        # print("assign", stack)
        e = stack.pop()
        stack.pop()
        token, raw = stack.pop()
        i = self.NoCompileNode(f"{raw}")
        return self.assign_node("assign", [i, e])

    def repeat(self, stack: Stack) -> Node:
        # print("repeat", stack)

        e = stack.pop()
        stack.pop()
        seq = stack.pop()
        stack.pop()
        return self.repeat_node("repeat", [seq, e])

    def if_no_else(self, stack: Stack) -> Node:
        # print("if_no_else", stack)
        stack.pop()
        seq = stack.pop()
        stack.pop()
        e = stack.pop()
        stack.pop()
        return self.if_node("if", [e, seq])

    def if_stmt(self, stack: Stack) -> Node:
        # print("if_stmt", stack)
        stack.pop()
        else_seq = stack.pop()
        stack.pop()
        seq = stack.pop()
        stack.pop()
        e = stack.pop()
        stack.pop()
        return self.if_node("if", [e, seq, else_seq])
