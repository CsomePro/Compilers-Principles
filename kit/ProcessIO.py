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
import json
import subprocess
from typing import List


def popen(cmd: List) -> subprocess.Popen:
    st = subprocess.STARTUPINFO()
    st.dwFlags = subprocess.STARTF_USESHOWWINDOW
    st.wShowWindow = subprocess.SW_HIDE
    p = subprocess.Popen(cmd, cwd='.', stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
                         , startupinfo=st)
    return p


if __name__ == '__main__':
    pc = popen(["sh"])
    inp = {"data": "data"}
    output, err = pc.communicate(json.dumps(inp))
    output = json.loads(output)