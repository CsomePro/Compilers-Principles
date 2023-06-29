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


import hashlib
import random

LETTER = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def getRandomString(k=4):
    return ''.join(random.choices(LETTER, k=k))

def getHash(s):
    return hashlib.sha256(s.encode()).hexdigest()[:10]

def dealWithConflict(data: dict, other: dict):
    assert 'raw' in data and 'raw' in other
    _, p0 = data['raw']
    _, p1 = other['raw']
    if p1 < p0:
        data.update(other)
    return data


def Set2Expr(st: set):
    ans = []
    for s in sorted(st):
        if s == "-":
            ans.extend("\\-")
            continue
        elif s == "\\":
            ans.extend("\\\\")
            continue
        if len(ans) < 2:
            ans.append(s)
            continue
        if ord(ans[-1]) == ord(ans[-2]) + 1 and ord(s) == ord(ans[-1]) + 1:
            ans[-1] = '-'
            ans.append(s)
        elif ord(ans[-1]) + 1 == ord(s) and ans[-2] == '-':
            ans[-1] = s
        else:
            ans.append(s)
    return "%s" % (repr(''.join(ans)).strip("'"))

if __name__ == '__main__':
    print(Set2Expr(set('abc-')))