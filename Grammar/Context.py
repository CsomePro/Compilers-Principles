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

import json
from typing import Dict, Any, List
import random
from .extand_compile_bytecode import compile_to_byte_code
import marshal

class Context:
    def __init__(self, sym: Dict[str, Any] = None, con: List = None, extra: Dict = None):
        if con is None:
            con = [None]
        if sym is None:
            sym = {}
        if extra is None:
            extra = {}
        self.symbol_table: Dict[str, Any] = sym
        self.const_table: List = con
        self.extra = extra
        self.names = []

    def setVar(self, name: str, args: Any):
        assert name not in self.symbol_table
        pos = self.getVarSize()
        self.symbol_table[name] = args
        return pos

    def getVar(self, name) -> Any:
        return self.symbol_table.get(name, None)

    def getVarSize(self):
        return len(self.symbol_table)

    def setConst(self, v) -> int:
        if v in self.const_table:
            return self.const_table.index(v)
        pos = len(self.const_table)
        self.const_table.append(v)
        return pos

    def setName(self, v) -> int:
        if v in self.names:
            return self.names.index(v)
        pos = len(self.names)
        self.names.append(v)
        return pos

    def getName(self, name):
        assert name in self.names
        return self.names.index(name)

    def testName(self, name):
        return name in self.names

    def setExtra(self, name, data):
        # assert name not in self.extra
        self.extra[name] = data

    def getExtra(self, name):
        return self.extra.get(name, None)

    def to_json(self):
        return {
                "sym_table": self.symbol_table,
                "const": self.const_table,
                "extra": self.extra
             }

    @staticmethod
    def getRandomStr(k):
        return "".join(random.choices("0987654321qwertyuioplkjhgfdsazxcvbnm", k=k))

    @staticmethod
    def compile_byte_code(code: List[str]):
        code = Context.label_compile(code)
        return compile_to_byte_code("\n".join(map(lambda x: f"{x[0]}\t\t{x[1]}", zip(range(0, len(code) * 2, 2), code))))

    @staticmethod
    def loads(b: bytes):
        return marshal.loads(b)

    @staticmethod
    def dumps(obj):
        return marshal.dumps(obj)

    @staticmethod
    def label_compile(code: [str]):
        label_map = {}
        release_code = []
        for s in code:
            s: str
            if s.startswith("label"):
                label = s[s.find("%") + 1:s.rfind("%")]
                label_map[label] = len(release_code)
                continue
            release_code.append(s)

        def exchange(x: str):
            if "%" in x:
                tmp = x[x.find("%") + 1:x.rfind("%")]
                y = str(label_map[tmp] * 2)
                return x[:x.find("%")] + y + x[x.rfind("%") + 1:]
            return x

        return list(map(exchange, release_code))