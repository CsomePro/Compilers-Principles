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


import dis
import json
from types import CodeType


def compile_to_byte_code(s):
    # data = json.loads('{"sym_table": {"x": [0, "int"], "fact": [1, "int"]}, "const": [null, 0, 1], "extra": {"co_globals": ["input", "int"]}}')
    # s ="""
    # 0		LOAD_GLOBAL 1 # (int)
    # 2		LOAD_GLOBAL 0 # (input)
    # 4		CALL_FUNCTION 0
    # 6		CALL_FUNCTION 1
    # 8		STORE_FAST 0 # (x)
    # 10		LOAD_CONST 1 # (0)
    # 12		LOAD_FAST 0 # (x)
    # 14		COMPARE_OP 0 # (<)
    # 16		POP_JUMP_IF_FALSE 50
    # 18		LOAD_CONST 2 # (1)
    # 20		STORE_FAST 1 # fact
    # 22		LOAD_FAST 1 # (fact)
    # 24		LOAD_FAST 0 # (x)
    # 26		BINARY_MULTIPLY
    # 28		STORE_FAST 1 # fact
    # 30		LOAD_FAST 0 # (x)
    # 32		LOAD_CONST 2 # (1)
    # 34		BINARY_SUBTRACT
    # 36		STORE_FAST 0 # x
    # 38		LOAD_FAST 0 # (x)
    # 40		LOAD_CONST 1 # (0)
    # 42		COMPARE_OP 2 # (==)
    # 44		POP_JUMP_IF_FALSE 22
    # 46		LOAD_FAST 1 # (fact)
    # 48		PRINT_EXPR
    # 50		LOAD_CONST 0 # (None)
    # 52		RETURN_VALUE
    # """.strip()
    code = bytearray()
    for x in s.split("\n"):
        tmp = x[:x.rfind("#")] if x.rfind("#") != -1 else x
        # print(tmp)
        idx, opname, *args = tmp.split()
        if args:
            args = int(args[0])
            args = args.to_bytes(byteorder="big", length=max(1, (args.bit_length() // 8) + (args.bit_length() != 0)))
            for b in args[:-1]:
                code.extend([dis.opmap['EXTENDED_ARG'], b])
            args = args[-1]
            code.extend([dis.opmap[opname], args])
            continue
        code.extend([dis.opmap[opname], 0])
    return code.hex()
    # print(dis.dis(code))

    # code = CodeType(0, 0, 0, len(co_sym), 0, 0, bytes(code), tuple(co_consts), tuple(co_globals), tuple(co_sym), "", "", 0, b'')
    # print(code)
    # dis.dis(code)
    # exec(code, {}, {})