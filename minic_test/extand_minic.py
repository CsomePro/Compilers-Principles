import types

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
            # print(self.name, self.child)
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
            assert 1 != 1, "No Compile!"

    class NoActionNode(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            return []

    class program_node(SelfNode):
        """
        生成最后的program之前必要的动作
        """

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("program_node", self)
            assert local_c is None
            seq: Node = self.child[0]
            code: [str] = seq.compile(global_c, None)
            release_code = Context.label_compile(code)
            main_func_idx = global_c.getName("main")
            release_code.extend([
                # f"LOAD_FAST {0}",
                # # f"CALL_FUNCTION 0",
                # f"PRINT_EXPR",
                f"LOAD_DEREF {main_func_idx}",
                f"CALL_FUNCTION 0",
                # f"LOAD_CONST 0",
                "RETURN_VALUE"
            ])
            # # print("program: log ", release_code)
            code_bytes = bytes.fromhex(Context.compile_byte_code(release_code))
            co_varnames = [_[0] for _ in (sorted(global_c.symbol_table.items(), key=lambda x: x[1][0]))]
            co_consts = global_c.const_table
            co_names = global_c.names
            # co_names.remove("main")
            # print("log program", co_names, co_varnames, co_consts)
            # co_lnotab = b"\x10\x01" * (len(code_bytes) // 16)
            co_lnotab = b""
            code_exec = types.CodeType(0, 0, 0, 1, 256, 3, code_bytes, tuple(co_consts), (), tuple(co_varnames),
                                       "", "_main", 0, co_lnotab, (), tuple(co_names))

            # code_bytes = bytes.fromhex(Context.compile_byte_code([
            #     "LOAD_CONST 0",
            #     "LOAD_CONST 1",
            #     "MAKE_FUNCTION 0",
            #     "STORE_NAME 0",
            #     "LOAD_NAME 0",
            #     "CALL_FUNCTION 0",
            #     "RETURN_VALUE"
            # ]))
            # code_exec2 = types.CodeType(0, 0, 0, 0, 256, 64, code_bytes, (code_exec, "_main"), ("_main", ),
            #                             (),
            #                            "", "", 0, b'')

            return code_exec

    class definition_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("definition_node", self)
            ans = []
            for ch in self.child:
                ch: Node
                # print("def: ", ans, ch)
                ans.extend(ch.compile(global_c, local_c))
                # print("def: ", ans)
            return ans

    class var_def_node(SelfNode):
        """
        type:id
        type[size]:id
        """

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("var_def_node", self)
            self.name: str
            store_context = local_c if local_c else global_c
            if "[" in self.name:
                ty = self.name[:self.name.find("[")]
                size = int(self.name[self.name.find("[") + 1: self.name.find("]")])
                idf = self.name[self.name.find(":") + 1:]
                zero_const = store_context.setConst(0)
                idx = store_context.getVarSize()
                store_context.setVar(idf, (idx, f"{ty}[{size}]"))
                return [f"LOAD_CONST {zero_const}"] * size + [
                    f"BUILD_LIST {size}",
                    f"STORE_FAST {idx} # {idf}"
                ]
            else:
                ty = self.name[:self.name.find(":")]
                idf = self.name[self.name.find(":") + 1:]
                idx = store_context.getVarSize()
                store_context.setVar(idf, (idx, f"{ty}"))
                return []

    class func_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("func_node", self)
            self.name: str
            assert local_c is None, "function closure error"
            ty = self.name[:self.name.find("(")]
            idf = self.name[self.name.find(":") + 1:]
            param: Node = self.child[0]
            compound: Node = self.child[1]
            lc = Context()
            lc.setExtra("args", set())
            lc.setExtra("globals", [])
            param.compile(None, lc)  # param不能接触到全局Context
            compound_code = compound.compile(global_c, lc)
            # print("func ", compound_code)
            # if idf == "main":
                # compound_code = ["LOAD_CONST 0", "PRINT_EXPR"] + compound_code
                # print("main", compound_code)
            code_bytes = bytes.fromhex(Context.compile_byte_code(compound_code))
            co_varnames = [_[0] for _ in (sorted(lc.symbol_table.items(), key=lambda x: x[1][0]))]
            co_consts = lc.const_table
            co_names = lc.names
            # print("function log: ", idf, co_names, co_consts, co_varnames)
            # co_lnotab = b"\x10\x01" * (len(code_bytes) // 16)
            co_lnotab = b''
            code_exec = types.CodeType(len(lc.getExtra("args")), 0, 0, len(co_varnames), 256, 0 if co_names else 0, code_bytes, tuple(co_consts), (),
                                       tuple(co_varnames),
                                       "", idf, 0, co_lnotab, tuple(co_names), ())
            func_call_name_idx = global_c.setName(idf)
            # return [
            #     *compound_code,
            # ]
            code_obj_idx = global_c.setConst(code_exec)
            func_name_idx = global_c.setConst(idf)
            if len(co_names) != 0:
                return [f"LOAD_CLOSURE {global_c.getName(name)}" for name in co_names] + [
                    f"BUILD_TUPLE {len(co_names)}",
                    f"LOAD_CONST {code_obj_idx}",
                    f"LOAD_CONST {func_name_idx}",
                    f"MAKE_FUNCTION 8",
                ] + ([f"STORE_DEREF {func_call_name_idx}"])
            else:
                return [
                    f"LOAD_CONST {code_obj_idx}",
                    f"LOAD_CONST {func_name_idx}",
                    f"MAKE_FUNCTION 0",
                ] + ([f"STORE_DEREF {func_call_name_idx}"])

    class param_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("param_node", self)
            assert global_c is None
            if self.name == "param-list":
                for ch in self.child:
                    ch: Node
                    ch.compile(None, local_c)
            else:
                ty = self.name[:self.name.find(":")]
                idf = self.name[self.name.find(":")+1:]
                # local_c.setName(idf)
                idx = local_c.getVarSize()
                local_c.setVar(idf, (idx, ty))
                args: set = local_c.getExtra("args")
                assert args is not None
                args.add(idf)
                local_c.setExtra("args", args)
            return []

    class compound_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("compound_node", self)
            ans = []
            for ch in self.child:
                ch: Node
                ans.extend(ch.compile(global_c, local_c))
            return ans

    class statement_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("statement_node", self)
            ans = []
            for ch in self.child:
                ch: Node
                ans.extend(ch.compile(global_c, local_c))
            return ans

    class if_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("if_node", self)
            if len(self.child) == 2:
                exp: Node = self.child[0]
                stmt: Node = self.child[1]
                exp_code = exp.compile(global_c, local_c)
                stmt_code = stmt.compile(global_c, local_c)
                end_label = "if_end_" + Context.getRandomStr(4)
                return [
                    *exp_code,
                    f"POP_JUMP_IF_FALSE %{end_label}%",
                    *stmt_code,
                    f"label %{end_label}%",
                ]
            elif len(self.child) == 3:
                exp: Node = self.child[0]
                true_part: Node = self.child[1]
                false_part: Node = self.child[2]
                exp_code = exp.compile(global_c, local_c)
                true_code = true_part.compile(global_c, local_c)
                false_code = false_part.compile(global_c, local_c)
                false_label = "if_false_" + Context.getRandomStr(4)
                end_label = "if_end_" + Context.getRandomStr(4)
                return [
                    *exp_code,
                    f"POP_JUMP_IF_FALSE %{end_label}%",
                    *true_code,
                    f"JUMP_ABSOLUTE %{end_label}%",
                    f"label %{false_label}%",
                    *false_code,
                    f"label %{end_label}%",
                ]
            else:
                assert 1 != 1, "Unknown"

    class while_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("while_node", self)
            stmt: Node = self.child[0]
            exp: Node = self.child[1]
            stmt_code = stmt.compile(global_c, local_c)
            exp_code = exp.compile(global_c, local_c)
            entry_label = "repeat_" + Context.getRandomStr(4)
            return [
                f"label %{entry_label}%",
                *stmt_code,
                *exp_code,
                f"POP_JUMP_IF_TRUE %{entry_label}%"
            ]

    class return_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("return_node", self)
            if len(self.child) == 0:
                none_id = local_c.setConst(None)
                return [f"LOAD_CONST {none_id}", "RETURN_VALUE"]
            elif len(self.child) == 1:
                exp = self.child[0]
                exp_code = exp.compile(global_c, local_c)
                return [
                    *exp_code,
                    "RETURN_VALUE"
                ]

    class assign_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("assign_node", self)
            if self.name == "assign":
                idf_node, exp = self.child
                idf_node: Node
                exp: Node
                exp_code = exp.compile(global_c, local_c)
                idf = idf_node.name

                if local_c is None:
                    idx, _ = global_c.getVar(idf)
                    return [
                        *exp_code,
                        f"STORE_DEREF {idx}"
                    ]
                elif local_c.getVar(idf) is not None:
                    idx, t = local_c.getVar(idf)
                    return [
                        *exp_code,
                        f"STORE_FAST {idx}"
                    ]
                # elif local_c.getExtra('args') is not None and idf in local_c.getExtra('args'):
                #     idx = local_c.setName(idf)
                #     return [
                #         *exp_code,
                #         f"STORE_NAME {idx}"
                #     ]
                else:

                    idx = local_c.setName(idf)
                    return [
                        *exp_code,
                        f"STORE_DEREF {idx}"
                    ]
            else:
                idf_node, sub, exp = self.child
                idf_node: Node
                exp: Node
                sub: Node
                sub_code = sub.compile(global_c, local_c)
                exp_code = exp.compile(global_c, local_c)
                idf = idf_node.name

                if local_c is None:
                    idx = global_c.getName(idf)
                    return [
                        *exp_code,
                        f"LOAD_DEREF {idx}",
                        *sub_code,
                        f"STORE_SUBSCR"
                    ]
                elif local_c.getVar(idf) is not None:
                    idx, t = local_c.getVar(idf)
                    return [
                        *exp_code,
                        f"LOAD_FAST {idx}",
                        *sub_code,
                        f"STORE_SUBSCR"
                    ]
                # elif local_c.getExtra('args') is not None and idf in local_c.getExtra('args'):
                #     idx = local_c.setName(idf)
                #     return [
                #         *sub_code,
                #         f"LOAD_NAME {idx}",
                #         *exp_code,
                #         f"STORE_SUBSCR"
                #     ]
                else:
                    idx = local_c.setName(idf)
                    # gs = local_c.getExtra("globals")
                    # if idf not in gs:
                    #     local_c.setExtra("globals", gs + [idf])
                    return [
                        *exp_code,
                        f"LOAD_DEREF {idx}",
                        *sub_code,
                        f"STORE_SUBSCR"
                    ]


    class var_node(SelfNode):
        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("var_node", self)
            idf = self.name[self.name.find(":") + 1:]

            if local_c is None:
                idx = global_c.getName(idf)
                if "[]" not in self.name:
                    return [f"LOAD_DEREF {idx}"]
                else:
                    exp: Node = self.child[0]
                    exp_code = exp.compile(global_c, local_c)
                    return [
                        f"LOAD_DEREF {idx}",
                        *exp_code,
                        "BINARY_SUBSCR"
                    ]

            if local_c.getVar(idf) is not None:
                idx, _ = local_c.getVar(idf)
                if "[]" not in self.name:
                    return [f"LOAD_FAST {idx}"]
                else:
                    exp: Node = self.child[0]
                    exp_code = exp.compile(global_c, local_c)
                    return [
                        f"LOAD_FAST {idx}",
                        *exp_code,
                        "BINARY_SUBSCR"
                    ]

            # if local_c.getExtra('args') is not None:
            #     if idf in local_c.getExtra('args'):
            #         idx = local_c.setName(idf)
            #         if "[]" not in self.name:
            #             return [f"LOAD_NAME {idx}"]
            #         else:
            #             exp: Node = self.child[0]
            #             exp_code = exp.compile(global_c, local_c)
            #             return [
            #                 f"LOAD_NAME {idx}",
            #                 *exp_code,
            #                 "BINARY_SUBSCR"
            #             ]

            idx = local_c.setName(idf)
            if "[]" not in self.name:
                return [f"LOAD_DEREF {idx}"]
            else:
                exp: Node = self.child[0]
                exp_code = exp.compile(global_c, local_c)
                return [
                    f"LOAD_DEREF {idx}",
                    *exp_code,
                    "BINARY_SUBSCR"
                ]

    class exp_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("exp_node", self)
            # [(0, '<'), (1, '<='), (2, '=='), (3, '!='), (4, '>'),
            # (5, '>='), (6, 'in'), (7, 'not in'), (8, 'is'), (9, 'is not'),
            # (10, 'exception match'), (11, 'BAD')]

            return {
                "+": lambda lc, rc: lc + rc + ["BINARY_ADD"],
                "-": lambda lc, rc: lc + rc + ["BINARY_SUBTRACT"],
                "*": lambda lc, rc: lc + rc + ["BINARY_MULTIPLY"],
                "/": lambda lc, rc: lc + rc + ["BINARY_FLOOR_DIVIDE"],
                "%": lambda lc, rc: lc + rc + ["BINARY_MODULO"],
                "==": lambda lc, rc: lc + rc + ["COMPARE_OP 2 # (==)"],
                "<": lambda lc, rc: lc + rc + ["COMPARE_OP 0 # (<)"],
                "<=": lambda lc, rc: lc + rc + ["COMPARE_OP 1 # (<=)"],
                ">": lambda lc, rc: lc + rc + ["COMPARE_OP 4 # (>)"],
                ">=": lambda lc, rc: lc + rc + ["COMPARE_OP 5 # (>=)"],
                "!=": lambda lc, rc: lc + rc + ["COMPARE_OP 3 # (!=)"],
            }[self.name](
                self.child[0].compile(global_c, local_c),
                self.child[1].compile(global_c, local_c)
            )

    class const_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("const_node", self)
            number = int(self.name)
            if local_c is None:
                idx = global_c.setConst(number)
            else:
                idx = local_c.setConst(number)
            return [f"LOAD_CONST {idx}"]

    class call_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("call_node", self)
            idf = self.name[:self.name.rfind("(")]
            if "()" in self.name:
                if local_c is None:
                    idx = global_c.getName(idf)
                    return [
                        f"LOAD_DEREF {idx}",
                        f"CALL_FUNCTION 0"
                    ]
                else:
                    idx = local_c.setName(idf)
                    return [
                        f"LOAD_DEREF {idx}",
                        f"CALL_FUNCTION 0"
                    ]
            elif "(*)" in self.name:
                args: Node = self.child[0]
                if args.name == 'args-list':
                    argn = len(args.child)
                else:
                    argn = 1
                arg_code = args.compile(global_c, local_c)
                if local_c is None:
                    idx = global_c.getName(idf)
                    return [
                        f"LOAD_DEREF {idx}",
                        *arg_code,
                        f"CALL_FUNCTION {argn}"
                    ]
                else:
                    idx = local_c.setName(idf)
                    return [
                        f"LOAD_DEREF {idx}",
                        *arg_code,
                        f"CALL_FUNCTION {argn}"
                    ]

    class args_node(SelfNode):

        def compile(self, global_c: Context, local_c: Context) -> []:
            # print("args_node", self)
            ans = []
            for ch in self.child:
                ch: Node
                ans.extend(ch.compile(global_c, local_c))
            return ans

    def program(self, stack: Stack) -> Node:
        # print("program", stack)
        return self.program_node("program", [stack.pop()])

    def definition(self, stack: Stack) -> Node:
        # print("definition", stack)
        n0 = stack.pop()
        n1 = stack.pop()
        if n1.name != "def-list":
            return self.definition_node("def-list", [n1, n0])
        n1.child.append(n0)
        return n1

    def var_3(self, stack: Stack) -> Node:
        # print("var_3", stack)
        assert stack.pop()[0] == "SEM"
        _, raw = stack.pop()  # ID
        _, t = stack.pop()  # Type
        return self.var_def_node(f"{t}:{raw}")

    def var_6(self, stack: Stack) -> Node:
        # print("var_6", stack)
        assert stack.pop()[0] == "SEM"
        assert stack.pop()[0] == "RSB"
        _, size = stack.pop()
        assert stack.pop()[0] == "LSB"
        _, raw = stack.pop()  # ID
        _, t = stack.pop()  # Type
        return self.var_def_node(f"{t}[{size}]:{raw}")

    def func_def(self, stack: Stack) -> Node:
        # print("func_def", stack)
        com_stmt = stack.pop()
        assert stack.pop()[0] == "RP"
        param = stack.pop()
        if isinstance(param, tuple):
            param = self.NoActionNode(f"{param[1]}")
        assert stack.pop()[0] == "LP"
        _, identify = stack.pop()
        _, ty = stack.pop()
        return self.func_node(f"{ty}(*):{identify}", [param, com_stmt])

    def param_list(self, stack: Stack) -> Node:
        # print("param_list", stack)
        p0 = stack.pop()
        assert stack.pop()[0] == "COM"
        p1 = stack.pop()
        if p1.name != "param-list":
            return self.param_node("param-list", [p1, p0])
        p1.child.append(p0)
        return p1

    def param_id(self, stack: Stack) -> Node:
        # print("param_id", stack)
        _, idf = stack.pop()
        _, ty = stack.pop()
        return self.param_node(f"{ty}:{idf}")

    def param_array(self, stack: Stack) -> Node:
        # print("param_array", stack)
        assert stack.pop()[0] == "RSB"
        assert stack.pop()[0] == "LSB"
        _, idf = stack.pop()
        _, ty = stack.pop()
        return self.param_node(f"{ty}[]:{idf}")

    def compound_4(self, stack: Stack) -> Node:
        # print("compound_4", stack)
        assert stack.pop()[0] == "CB"
        stmt = stack.pop()
        lc = stack.pop()
        assert stack.pop()[0] == "OB"
        return self.compound_node("compound", [lc, stmt])

    def compound_3(self, stack: Stack) -> Node:
        # print("compound_3", stack)
        assert stack.pop()[0] == "CB"
        lc = stack.pop()
        assert stack.pop()[0] == "OB"
        return self.compound_node("compound", [lc])

    def compound_2(self, stack: Stack) -> Node:
        # print("compound_2", stack)
        assert stack.pop()[0] == "CB"
        stmt = stack.pop()
        assert stack.pop()[0] == "OB"
        return self.compound_node("compound", [stmt])

    def compound_1(self, stack: Stack) -> Node:
        # print("compound_1", stack)
        assert stack.pop()[0] == "CB"
        assert stack.pop()[0] == "OB"
        return self.compound_node("compound", [])

    def local_list(self, stack: Stack) -> Node:
        # print("local_list", stack)
        v_def = stack.pop()
        loc = stack.pop()
        if loc.name != "def-list":
            return self.definition_node("def-list", [loc, v_def])
        loc.child.append(v_def)
        return loc

    def stmt_list(self, stack: Stack) -> Node:
        # print("stmt_list", stack)
        s0 = stack.pop()
        s1 = stack.pop()
        if s1.name != "stmt-list":
            return self.statement_node("stmt-list", [s1, s0])
        s1.child.append(s0)
        return s1

    def exp_sem(self, stack: Stack) -> Node:
        # print("exp_sem", stack)
        assert stack.pop()[0] == "SEM"
        return stack.pop()

    def exp_empty(self, stack: Stack) -> Node:
        # print("exp_empty", stack)
        assert stack.pop()[0] == "SEM"
        return self.NoActionNode(f"<empty>")

    def if_stmt(self, stack: Stack) -> Node:
        # print("if_stmt", stack)
        stmt = stack.pop()
        assert stack.pop()[0] == "RP"
        exp = stack.pop()
        assert stack.pop()[0] == "LP"
        assert stack.pop()[0] == "IF"
        return self.if_node("if", [exp, stmt])

    def if_else(self, stack: Stack) -> Node:
        # print("if_else", stack)
        false_part = stack.pop()
        assert stack.pop()[0] == "ELSE"
        true_part = stack.pop()
        assert stack.pop()[0] == "RP"
        exp = stack.pop()
        assert stack.pop()[0] == "LP"
        assert stack.pop()[0] == "IF"
        return self.if_node("if", [exp, true_part, false_part])

    def while_stmt(self, stack: Stack) -> Node:
        # print("while_stmt", stack)
        assert stack.pop()[0] == "SEM"
        assert stack.pop()[0] == "RP"
        exp = stack.pop()
        assert stack.pop()[0] == "LP"
        assert stack.pop()[0] == "WHILE"
        stmt = stack.pop()
        assert stack.pop()[0] == "DO"
        return self.while_node("while", [stmt, exp])

    def return_void(self, stack: Stack) -> Node:
        # print("return_void", stack)
        assert stack.pop()[0] == "SEM"
        assert stack.pop()[0] == "RETURN"
        return self.return_node("return")

    def return_exp(self, stack: Stack) -> Node:
        # print("return_exp", stack)
        assert stack.pop()[0] == "SEM"
        exp = stack.pop()
        assert stack.pop()[0] == "RETURN"
        return self.return_node("return", [exp])

    def exp_assign_id(self, stack: Stack) -> Node:
        # print("exp_assign_id", stack)
        exp = stack.pop()
        assert stack.pop()[0] == "ASSIGN"
        _, idf = stack.pop()
        return self.assign_node(f"assign", [self.NoCompileNode(idf), exp])

    def exp_assign_array(self, stack: Stack) -> Node:
        # print("exp_assign_array", stack)
        exp = stack.pop()
        assert stack.pop()[0] == "ASSIGN"
        assert stack.pop()[0] == "RSB"
        exp1 = stack.pop()
        assert stack.pop()[0] == "LSB"
        _, idf = stack.pop()
        ans = self.assign_node(f"assign-array", [self.NoCompileNode(idf), exp1, exp])
        # # print(ans)
        return ans

    def var_id(self, stack: Stack) -> Node:
        # print("var_id", stack)
        _, idf = stack.pop()
        return self.var_node(f"var:{idf}")

    def var_array(self, stack: Stack) -> Node:
        # print("var_array", stack)
        assert stack.pop()[0] == "RSB"
        exp = stack.pop()
        assert stack.pop()[0] == "LSB"
        _, idf = stack.pop()
        return self.var_node(f"var[]:{idf}", [exp])

    def exp(self, stack: Stack) -> Node:
        # print("exp", stack)
        right = stack.pop()
        _, op = stack.pop()
        left = stack.pop()
        return self.exp_node(f"{op}", [left, right])

    def factor(self, stack: Stack) -> Node:
        # print("factor", stack)
        assert stack.pop()[0] == "RP"
        exp = stack.pop()
        assert stack.pop()[0] == "LP"
        return exp

    def factor_const(self, stack: Stack) -> Node:
        # print("factor_const", stack)
        _, number = stack.pop()
        return self.const_node(f"{number}")

    def call_non_arg(self, stack: Stack) -> Node:
        # print("call_non_arg", stack)
        assert stack.pop()[0] == "RP"
        assert stack.pop()[0] == "LP"
        _, idf = stack.pop()
        return self.call_node(f"{idf}()")

    def call_args(self, stack: Stack) -> Node:
        # print("call_args", stack)
        assert stack.pop()[0] == "RP"
        args = stack.pop()
        assert stack.pop()[0] == "LP"
        _, idf = stack.pop()
        return self.call_node(f"{idf}(*)", [args])

    def args_list(self, stack: Stack) -> Node:
        # print("args_list", stack)
        exp = stack.pop()
        assert stack.pop()[0] == "COM"
        args_list = stack.pop()
        if args_list.name != "args-list":
            return self.args_node("args-list", [args_list, exp])
        args_list.child.append(exp)
        return args_list
